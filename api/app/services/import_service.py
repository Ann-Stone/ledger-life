"""Background-task workers for stock-price, FX-rate, and invoice imports.

All workers create their own `Session(engine)` per `api/CLAUDE.md §6` — they
must not reuse the request session. Failures are logged and never raise.
"""
from __future__ import annotations

import csv
import io
import json
import logging
import random
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable

from sqlmodel import Session, select

from app.config import settings
from app.database import engine
from app.models.assets.stock import StockJournal
from app.models.dashboard.fx_rate import FXRate
from app.models.dashboard.stock_price_history import StockPriceHistory
from app.models.monthly_report.journal import Journal
from app.models.settings.credit_card import CreditCard
from app.models.utilities.imports import (
    InvoiceImportError,
    InvoiceImportMonth,
    InvoiceImportResult,
)

logger = logging.getLogger(__name__)


# ---------- Config loaders ----------


def load_invoice_skip_list(path: str) -> list[str]:
    p = Path(path)
    if not p.exists():
        logger.warning("Invoice skip list not found: %s", path)
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [str(x) for x in data]
        logger.error("Invoice skip list must be a JSON array: %s", path)
        return []
    except json.JSONDecodeError as e:
        logger.error("Invoice skip list invalid JSON (%s): %s", path, e)
        return []


def load_merchant_mapping(path: str) -> dict[str, str]:
    p = Path(path)
    if not p.exists():
        logger.warning("Merchant mapping not found: %s", path)
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items()}
        logger.error("Merchant mapping must be a JSON object: %s", path)
        return {}
    except json.JSONDecodeError as e:
        logger.error("Merchant mapping invalid JSON (%s): %s", path, e)
        return {}


# ---------- Period helpers ----------


def _period_to_last_day(period: str) -> str:
    """Return YYYYMMDD of the last day of the requested YYYYMM, or today."""
    if not period:
        return date.today().strftime("%Y%m%d")
    base = datetime.strptime(period, "%Y%m").replace(day=28) + timedelta(days=4)
    last = base - timedelta(days=base.day)
    return last.strftime("%Y%m%d")


def _period_to_range(period: str) -> tuple[str, str]:
    """Return (start, end) ISO dates spanning the YYYYMM month.

    ``end`` is the first day of the *next* month; yfinance treats ``end`` as
    exclusive, so the window covers exactly the requested month. Callers fetch
    the window and take the last trading day = the month's real closing bar.
    """
    first = datetime.strptime(period, "%Y%m")
    nxt = (first.replace(day=28) + timedelta(days=4)).replace(day=1)
    return first.strftime("%Y-%m-%d"), nxt.strftime("%Y-%m-%d")


def _last_completed_month() -> str:
    """Return YYYYMM of the most recently completed month, relative to today."""
    first_of_this = date.today().replace(day=1)
    return (first_of_this - timedelta(days=1)).strftime("%Y%m")


def _yfinance_ticker(stock_code: str) -> str:
    """Heuristic: digits-only codes are TW listed → append .TW; others as-is.

    StockJournal does not store vesting_nation; this heuristic mirrors the
    legacy behavior in `globalRouter.py` which treated TW codes by suffix.
    """
    return f"{stock_code}.TW" if stock_code.isdigit() else stock_code


# ---------- Stock price import ----------


def _fetch_one_stock_price(
    session: Session, stock_code: str, fetch_date: str, period: str = ""
) -> bool:
    """Fetch + upsert a single ticker. Return True if a row was inserted/updated.

    With a ``period`` (YYYYMM) the month's historical bars are fetched and the
    last trading day's OHLC is used, so a past month is backfilled with its real
    month-end close rather than today's price. An empty ``period`` keeps the
    legacy "latest trading day" behavior.
    """
    try:
        import yfinance as yf  # imported lazily to keep test startup fast
    except ImportError:  # pragma: no cover
        logger.error("yfinance is required for import_stock_prices")
        return False

    ticker = _yfinance_ticker(stock_code)
    for attempt in range(3):
        try:
            if period:
                start_iso, end_iso = _period_to_range(period)
                data = yf.download(ticker, start=start_iso, end=end_iso, progress=False)
            else:
                data = yf.download(ticker, period="1d", progress=False)
            break
        except Exception as e:  # noqa: BLE001 — third-party flake
            msg = str(e)
            if "404" in msg:
                logger.warning("Stock 404, skipping: %s", ticker)
                return False
            if "429" in msg and attempt < 2:
                sleep_for = 2**attempt + random.uniform(1, 3)
                logger.warning("429 on %s, retry %d in %.1fs", ticker, attempt + 1, sleep_for)
                time.sleep(sleep_for)
                continue
            logger.error("Stock fetch failed for %s: %s", ticker, e)
            return False
    else:  # pragma: no cover — exhausted retries
        return False

    if data is None or len(data) == 0:
        return False
    row = data.iloc[-1]
    open_p = float(row["Open"]) if "Open" in row else 0.0
    high_p = float(row["High"]) if "High" in row else 0.0
    low_p = float(row["Low"]) if "Low" in row else 0.0
    close_p = float(row["Close"]) if "Close" in row else 0.0

    existing = session.exec(
        select(StockPriceHistory).where(
            StockPriceHistory.stock_code == stock_code,
            StockPriceHistory.fetch_date == fetch_date,
        )
    ).first()
    if existing is not None:
        existing.open_price = open_p
        existing.highest_price = high_p
        existing.lowest_price = low_p
        existing.close_price = close_p
        session.add(existing)
    else:
        session.add(
            StockPriceHistory(
                stock_code=stock_code,
                fetch_date=fetch_date,
                open_price=open_p,
                highest_price=high_p,
                lowest_price=low_p,
                close_price=close_p,
            )
        )
    session.commit()
    return True


def import_stock_prices(period: str) -> None:
    """Background worker: fetch + upsert daily prices for every distinct ticker."""
    fetch_date = _period_to_last_day(period)
    with Session(engine) as session:
        codes = list(
            {row.stock_code for row in session.exec(select(StockJournal)).all()}
        )
        for i, stock_code in enumerate(sorted(codes), start=1):
            try:
                _fetch_one_stock_price(session, stock_code, fetch_date, period)
            except Exception as e:  # noqa: BLE001
                logger.error("Unexpected stock import error for %s: %s", stock_code, e)
            if i % 10 == 0:
                time.sleep(3)


# ---------- FX rate import ----------


def _sinopac_url() -> str:
    ts = int(time.time() * 1000)
    return (
        "https://mma.sinopac.com/ws/share/rate/ws_exchange.ashx"
        f"?exchangeType=REMIT&_={ts}"
    )


def _upsert_fx(session: Session, import_date: str, code: str, buy_rate: float) -> None:
    existing = session.exec(
        select(FXRate).where(FXRate.import_date == import_date, FXRate.code == code)
    ).first()
    if existing is not None:
        existing.buy_rate = buy_rate
        session.add(existing)
    else:
        session.add(FXRate(import_date=import_date, code=code, buy_rate=buy_rate))


def _fetch_and_store_fx(import_date: str) -> None:
    """Fetch current Sinopac rates and upsert them all under ``import_date``."""
    try:
        import httpx

        with httpx.Client(verify=False, timeout=30.0) as cli:
            resp = cli.get(_sinopac_url())
            resp.raise_for_status()
            payload = resp.json()
    except Exception as e:  # noqa: BLE001
        logger.error("FX rate fetch failed: %s", e)
        return

    sub_info: Iterable[dict] = payload.get("SubInfo", []) or []
    with Session(engine) as session:
        for entry in sub_info:
            code = entry.get("DataValue4")
            buy_raw = entry.get("DataValue2")
            if not code or buy_raw in (None, ""):
                continue
            try:
                buy_rate = float(buy_raw)
            except (TypeError, ValueError):
                continue
            _upsert_fx(session, import_date, code, buy_rate)
        session.commit()


def import_fx_rates(period: str) -> None:
    """Background worker (manual path): store the current Sinopac quote.

    Sinopac only serves *today's* rate, so today's real date is the only honest
    label. For the ongoing month (today <= month-end) we store today; a past
    ``period`` is clamped to that month-end so it can still seed that month's
    settlement as a rough proxy. Empty ``period`` also stores today. Accurate
    backfill of a *past* month needs a historical source (Sinopac has none).
    """
    today = date.today().strftime("%Y%m%d")
    import_date = today if not period else min(today, _period_to_last_day(period))
    _fetch_and_store_fx(import_date)


# ---------- Startup auto catch-up ----------


def _has_stock_month_row(session: Session, stock_code: str, period: str) -> bool:
    """True if ``stock_code`` already has a price row within the YYYYMM month."""
    row = session.exec(
        select(StockPriceHistory).where(
            StockPriceHistory.stock_code == stock_code,
            StockPriceHistory.fetch_date >= f"{period}01",
            StockPriceHistory.fetch_date <= f"{period}31",
        )
    ).first()
    return row is not None


def _catch_up_fx() -> None:
    """Record today's FX rate at its true date, at most once per calendar day.

    Settlement's ``fx_rate_for_month`` (latest import_date <= month-end)
    then uses the most recent real rate on or before month-end — no look-ahead,
    no fabricated month-end quote.
    """
    today = date.today().strftime("%Y%m%d")
    with Session(engine) as session:
        already = session.exec(
            select(FXRate).where(FXRate.import_date == today)
        ).first()
    if already is not None:
        return
    _fetch_and_store_fx(today)


def _bot_fx_csv_url(ccy: str, span: str = "L6M") -> str:
    """Bank of Taiwan per-currency historical daily-rate CSV (last 6 months)."""
    return f"https://rate.bot.com.tw/xrt/flcsv/0/{span}/{ccy}"


def _fetch_bot_spot_buy_at_month_end(ccy: str, period: str) -> tuple[str, float] | None:
    """Return (YYYYMMDD, 即期買入) for BOT's latest business day on/before month-end.

    Bank of Taiwan publishes daily board rates; we take the spot-buy (即期買入)
    column — the rate for converting the currency back to TWD, same spirit as
    Sinopac's REMIT buy. Returns ``None`` when the CSV can't be fetched, the
    month-end predates the ~6-month window, or the currency has no spot quote.

    CSV columns (newest row first): 0=資料日期(YYYYMMDD) 1=幣別 2="本行買入"
    3=現金買入 4=即期買入 ... so the first row whose date is <= month-end wins.
    """
    month_end = _period_to_last_day(period)
    try:
        import httpx

        with httpx.Client(timeout=30.0) as cli:
            resp = cli.get(_bot_fx_csv_url(ccy))
            resp.raise_for_status()
            text = resp.text  # header row (incl. any UTF-8 BOM) is skipped below
    except Exception as e:  # noqa: BLE001
        logger.error("BOT FX fetch failed for %s: %s", ccy, e)
        return None

    for row in csv.reader(io.StringIO(text)):
        if len(row) < 5:
            continue
        day = row[0].strip()
        if not (day.isdigit() and len(day) == 8) or day > month_end:
            continue
        try:
            spot_buy = float(row[4])
        except (TypeError, ValueError):
            continue
        if spot_buy > 0:
            return day, spot_buy
    return None


def _catch_up_fx_history() -> None:
    """Backfill a fully-missed month's month-end rate from Bank of Taiwan.

    Sinopac stays primary: only currencies with NO rate at all inside the last
    completed month (i.e. the app was never opened that month) are backfilled,
    using BOT's spot-buy on/before month-end stored at its real date. Months the
    user did capture via Sinopac are left untouched.
    """
    period = _last_completed_month()
    month_end = _period_to_last_day(period)
    with Session(engine) as session:
        all_codes = {
            r.code
            for r in session.exec(select(FXRate)).all()
            if r.code and r.code != "TWD"
        }
        present = {
            r.code
            for r in session.exec(
                select(FXRate).where(
                    FXRate.import_date >= f"{period}01",
                    FXRate.import_date <= month_end,
                )
            ).all()
        }
    for ccy in sorted(all_codes - present):
        result = _fetch_bot_spot_buy_at_month_end(ccy, period)
        if result is None:
            continue
        bot_date, rate = result
        with Session(engine) as session:
            _upsert_fx(session, bot_date, ccy, rate)
            session.commit()


def _catch_up_stock() -> None:
    """Backfill the last completed month's close for any holding still missing it.

    The per-ticker missing-guard makes this idempotent and storm-safe: a partial
    run (e.g. some tickers 429'd) only re-fetches the ones still absent on the
    next launch.
    """
    period = _last_completed_month()
    fetch_date = _period_to_last_day(period)
    with Session(engine) as session:
        codes = sorted(
            {row.stock_code for row in session.exec(select(StockJournal)).all()}
        )
        pending = [c for c in codes if not _has_stock_month_row(session, c, period)]
        for i, stock_code in enumerate(pending, start=1):
            try:
                _fetch_one_stock_price(session, stock_code, fetch_date, period)
            except Exception as e:  # noqa: BLE001
                logger.error("Catch-up stock error for %s: %s", stock_code, e)
            if i % 10 == 0:
                time.sleep(3)


def startup_catch_up() -> None:
    """Best-effort month-end backfill, run in the background on app startup.

    Never raises. Three guarded steps, each idempotent so repeated launches do no
    redundant work:
      1. FX — log today's Sinopac rate at its true date (<= once/day).
      2. FX history — for a *fully missed* last month, backfill its month-end
         spot-buy from Bank of Taiwan (Sinopac stays primary; only empty months).
      3. Stock — fetch the last completed month's close for any holding missing
         it (<= once per month per ticker).
    This frees the user from manual monthly backfill; stock is always exact, and
    FX is exact at month-end whenever a month was either captured live or filled
    from BOT history.
    """
    try:
        _catch_up_fx()
    except Exception as e:  # noqa: BLE001
        logger.error("FX catch-up failed: %s", e)
    try:
        _catch_up_fx_history()
    except Exception as e:  # noqa: BLE001
        logger.error("FX history catch-up failed: %s", e)
    try:
        _catch_up_stock()
    except Exception as e:  # noqa: BLE001
        logger.error("Stock catch-up failed: %s", e)


# ---------- Invoice CSV import ----------


def _match_merchant(shop_name: str, mapping: dict[str, str]) -> str | None:
    """Case-insensitive substring match; first match wins (insertion order)."""
    if not shop_name:
        return None
    haystack = shop_name.lower()
    for keyword, target in mapping.items():
        if keyword and keyword.lower() in haystack:
            return target
    return None


def _append_error_log(message: str) -> None:
    log_path = Path(settings.invoice_error_log)
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as fp:
            fp.write(message + "\n")
    except OSError as e:
        logger.error("Cannot write invoice error log: %s", e)


def import_invoices(content: str) -> InvoiceImportResult:
    """Import an uploaded invoice CSV (pipe-delimited text) into Journal.

    `content` is the decoded text of the uploaded file. Every M-row is imported;
    rows whose carrier is in the skip list or whose (invoice_number,
    vesting_month) already exists are skipped, and per-row failures are collected
    (never raised). The previous disk-read path (``settings.import_csv``) and the
    period filter were removed when the page switched to direct file upload.
    """
    skip_list = load_invoice_skip_list(settings.invoice_skip_path)
    mapping = load_merchant_mapping(settings.merchant_mapping_path)

    imported = 0
    skipped = 0
    failed = 0
    errors: list[InvoiceImportError] = []
    pending_items: dict[str, list[str]] = {}
    month_imported: dict[str, int] = {}
    month_skipped: dict[str, int] = {}

    with Session(engine) as session:
        cards = session.exec(select(CreditCard)).all()
        # Map last-4-digits of card_no → CreditCard for a best-effort carrier
        # match. CreditCard.carrier_no was dropped per README Decision Log;
        # this is a best-effort fallback.
        card_by_last4: dict[str, CreditCard] = {}
        for c in cards:
            if c.card_no:
                tail = "".join(ch for ch in c.card_no if ch.isdigit())[-4:]
                if tail:
                    card_by_last4[tail] = c

        reader = csv.reader(io.StringIO(content), delimiter="|")
        m_rows: list[tuple[int, list[str]]] = []
        for line_no, row in enumerate(reader, start=1):
            if not row:
                continue
            kind = row[0].strip() if row else ""
            if kind == "M":
                m_rows.append((line_no, row))
            elif kind == "D" and len(row) >= 4:
                inv = row[1].strip()
                pending_items.setdefault(inv, []).append(row[3].strip())

        for line_no, row in m_rows:
            try:
                if len(row) < 8:
                    raise ValueError("M-row missing columns")
                carrier_no = row[2].strip()
                invoice_date = row[3].strip()
                shop_name = row[5].strip() if len(row) > 5 else ""
                invoice_number = row[6].strip() if len(row) > 6 else ""
                amount = int(row[7]) * -1
                vesting_month = invoice_date[:6]
                if not vesting_month or len(vesting_month) != 6:
                    raise ValueError("invoice_date missing")
                if carrier_no in skip_list:
                    skipped += 1
                    month_skipped[vesting_month] = month_skipped.get(vesting_month, 0) + 1
                    continue
                existing = session.exec(
                    select(Journal).where(
                        Journal.invoice_number == invoice_number,
                        Journal.vesting_month == vesting_month,
                    )
                ).first()
                if existing is not None:
                    skipped += 1
                    month_skipped[vesting_month] = month_skipped.get(vesting_month, 0) + 1
                    continue

                spend_way = ""
                spend_way_type = ""
                spend_way_table = ""
                carrier_tail = "".join(ch for ch in carrier_no if ch.isdigit())[-4:]
                card = card_by_last4.get(carrier_tail) if carrier_tail else None
                if card is not None:
                    spend_way = card.credit_card_id
                    spend_way_type = "credit_card"
                    spend_way_table = "Credit_Card"

                action_main = _match_merchant(shop_name, mapping) or ""
                item_names = pending_items.get(invoice_number, [])
                note = ", ".join(filter(None, item_names)) or shop_name

                journal = Journal(
                    vesting_month=vesting_month,
                    spend_date=invoice_date,
                    spend_way=spend_way,
                    spend_way_type=spend_way_type,
                    spend_way_table=spend_way_table,
                    action_main=action_main,
                    action_main_type="Floating" if action_main else "",
                    action_main_table="Code_Data",
                    action_sub=None,
                    action_sub_type=None,
                    action_sub_table=None,
                    spending=float(amount),
                    invoice_number=invoice_number or None,
                    note=note or None,
                )
                session.add(journal)
                imported += 1
                month_imported[vesting_month] = month_imported.get(vesting_month, 0) + 1
            except Exception as e:  # noqa: BLE001
                failed += 1
                errors.append(InvoiceImportError(line=line_no, reason=str(e)))
                _append_error_log(f"line {line_no}: {e}")
        session.commit()

    all_months = sorted(set(month_imported) | set(month_skipped))
    months = [
        InvoiceImportMonth(
            month=m,
            imported=month_imported.get(m, 0),
            skipped=month_skipped.get(m, 0),
        )
        for m in all_months
    ]

    return InvoiceImportResult(
        imported=imported, skipped=skipped, failed=failed, months=months, errors=errors
    )
