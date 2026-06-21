"""Stock service: month close-price selection, holdings projection, manual/yfinance insert.

Used by the BE-018 stock-price endpoints and reused by the BE-019 stock
settlement step.
"""
from __future__ import annotations

import time

from sqlmodel import Session, select

from app.models.assets.stock import (
    StockDetail,
    StockJournal,
    StockPnlSummaryRead,
)
from app.models.dashboard.stock_price_history import StockPriceHistory
from app.models.monthly_report.stock_price import (
    StockPriceCreate,
    StockPriceMonthRead,
)
from app.models.settings.account import Account
from app.services.fx_lookup import BASE_CURRENCY
from app.services.month_utils import month_end, month_start, shift_month


def select_in_month_close_price(
    session: Session, stock_code: str, vesting_month: str
) -> StockPriceHistory | None:
    """Pick the most recent ``StockPriceHistory`` row *within* the requested month.

    Unlike :func:`select_month_close_price`, this never falls back to prior
    months. Returns ``None`` when the month itself has no price row, so callers
    can surface a blank and know a fetch is needed.
    """
    stmt = (
        select(StockPriceHistory)
        .where(StockPriceHistory.stock_code == stock_code)
        .where(StockPriceHistory.fetch_date >= month_start(vesting_month))
        .where(StockPriceHistory.fetch_date <= month_end(vesting_month))
        .order_by(StockPriceHistory.fetch_date.desc())
    )
    return session.exec(stmt).first()


def select_month_close_price(
    session: Session, stock_code: str, vesting_month: str
) -> StockPriceHistory | None:
    """Pick the most recent ``StockPriceHistory`` row for a ticker on or before month-end.

    If the month has no row, fall back to the most recent prior row. Returns
    ``None`` only when no row at all exists for that ticker.
    """
    in_month = (
        select(StockPriceHistory)
        .where(StockPriceHistory.stock_code == stock_code)
        .where(StockPriceHistory.fetch_date <= month_end(vesting_month))
        .order_by(StockPriceHistory.fetch_date.desc())
    )
    row = session.exec(in_month).first()
    if row is not None:
        return row
    fallback = (
        select(StockPriceHistory)
        .where(StockPriceHistory.stock_code == stock_code)
        .order_by(StockPriceHistory.fetch_date.desc())
    )
    return session.exec(fallback).first()


def list_month_stock_prices(
    session: Session, vesting_month: str
) -> list[StockPriceMonthRead]:
    """Return each held stock's in-month close price for the requested month.

    The price window is strictly the requested month: only a row whose
    ``fetch_date`` falls within ``{vesting_month}01``..``{vesting_month}31`` is
    used (no fallback to prior months). When the month has no row for a holding
    the row is still emitted with ``close_price`` / ``fetch_date`` set to
    ``None`` — that blank tells the caller to fetch a fresh price for that month.
    """
    holdings = list(session.exec(select(StockJournal)).all())
    out: list[StockPriceMonthRead] = []
    for h in holdings:
        price = select_in_month_close_price(session, h.stock_code, vesting_month)
        out.append(
            StockPriceMonthRead(
                stock_code=h.stock_code,
                stock_name=h.stock_name,
                close_price=price.close_price if price is not None else None,
                fetch_date=price.fetch_date if price is not None else None,
            )
        )
    return out


def fetch_yfinance_price(stock_code: str, fetch_date: str) -> float:
    """Fetch the close price for ``stock_code`` on ``fetch_date`` (YYYYMMDD).

    Retries up to 3 times with exponential backoff. Raises ``RuntimeError``
    after all retries are exhausted.
    """
    import yfinance  # local import; mocked in tests

    last_exc: Exception | None = None
    for attempt in range(3):
        try:
            ticker = yfinance.Ticker(stock_code)
            iso = f"{fetch_date[:4]}-{fetch_date[4:6]}-{fetch_date[6:8]}"
            history = ticker.history(start=iso, end=iso, interval="1d")
            if history is None or len(history) == 0:
                raise RuntimeError(f"No yfinance data for {stock_code} on {fetch_date}")
            close = float(history["Close"].iloc[-1])
            return close
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            time.sleep(0.1 * (2 ** attempt))
    raise RuntimeError(f"yfinance fetch failed for {stock_code}: {last_exc}")


def insert_stock_price(
    session: Session, payload: StockPriceCreate
) -> StockPriceHistory:
    """Persist a ``StockPriceHistory`` row, optionally overwriting close via yfinance."""
    from fastapi import HTTPException

    data = payload.model_dump()
    trigger = data.pop("trigger_yfinance", False)
    if trigger:
        try:
            data["close_price"] = fetch_yfinance_price(
                data["stock_code"], data["fetch_date"]
            )
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail=f"yfinance fetch failed: {exc}")
    row = StockPriceHistory(**data)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


# ---------- Per-stock P&L summary (asset-management columns) ----------

_EPS = 1e-6


def _holding_fx_code(session: Session, rows: list[StockDetail]) -> str:
    """Resolve the currency a holding is denominated in.

    Mirrors ``run_stock_step``: take the settling account of the most recent
    detail row; fall back to the base currency when unknown.
    """
    if not rows:
        return BASE_CURRENCY
    account = session.exec(
        select(Account).where(Account.account_id == rows[-1].account_id)
    ).first()
    if account is not None and account.fx_code:
        return account.fx_code
    return BASE_CURRENCY


def compute_stock_pnl_summary(
    session: Session, asset_id: str, as_of_month: str
) -> list[StockPnlSummaryRead]:
    """Per-holding cost / market value / realized / unrealized / yields.

    Derived fresh from ``Stock_Detail`` (the only per-stock source — realized and
    dividend journals are not keyed to a ``stock_id``). Driven by ``excute_type``
    with ``abs()`` magnitudes so the result is correct regardless of which write
    path produced the row (the asset-manage and cashflow-sync paths disagree on
    the sign of amount).

    ``excute_price`` is the **whole-transaction cash amount, fees included**, not
    a per-share price (a buy of 10 shares for 1,805 stores 1,805, not 180.5) — so
    a buy adds its full amount to cost and a sell's realized gain is its net
    proceeds minus the average cost of the shares sold. Fees therefore raise cost
    basis and lower realized automatically. Cost uses a moving-average basis: a
    sell does not change the remaining shares' average, it just realises the gain
    at the average-at-that-moment, so each realised slice is locked in. Money is
    reported in each holding's own ``fx_code`` (no base-currency conversion).

    Note: this realized figure will not necessarily tie out to the income
    statement's ``realized`` (booked 資本利得 journals) — there is no per-stock
    source for that, so a clean recomputation is the only option.
    """
    upper = month_end(as_of_month)
    # Trailing-12-month window for the cash-dividend yield: 12 inclusive months
    # ending at as_of_month (e.g. 202606 → 20250701 .. 20260631).
    ttm_cutoff = month_start(shift_month(as_of_month, -11))

    holdings = list(
        session.exec(
            select(StockJournal).where(StockJournal.asset_id == asset_id)
        ).all()
    )
    out: list[StockPnlSummaryRead] = []
    for h in holdings:
        rows = list(
            session.exec(
                select(StockDetail)
                .where(StockDetail.stock_id == h.stock_id)
                .where(StockDetail.excute_date <= upper)
                .order_by(
                    StockDetail.excute_date.asc(),
                    StockDetail.distinct_number.asc(),
                )
            ).all()
        )

        shares = 0.0
        total_cost = 0.0
        realized = 0.0
        dividends_total = 0.0
        ttm_dividends = 0.0
        for r in rows:
            amt = abs(r.excute_amount)
            total = abs(r.excute_price)  # whole-transaction amount, fees included
            if r.excute_type == "buy":
                shares += amt
                total_cost += total
            elif r.excute_type == "stock":
                shares += amt  # stock dividend / split: shares up, cost flat
            elif r.excute_type == "sell":
                avg = total_cost / shares if shares > _EPS else 0.0
                cost_out = avg * amt  # average cost of the shares sold
                realized += total - cost_out  # net proceeds − cost of sold shares
                total_cost -= cost_out
                shares -= amt
            elif r.excute_type == "cash":
                dividends_total += total
                if r.excute_date >= ttm_cutoff:
                    ttm_dividends += total

        if abs(shares) < _EPS:
            shares = 0.0
            total_cost = 0.0
        cost = total_cost

        price_row = select_month_close_price(session, h.stock_code, as_of_month)
        close_price = price_row.close_price if price_row is not None else None
        price_date = price_row.fetch_date if price_row is not None else None

        market_value: float | None
        unrealized: float | None
        unrealized_pct: float | None
        if shares == 0.0:
            market_value = 0.0
            unrealized = 0.0
            unrealized_pct = None
        elif close_price is not None:
            market_value = shares * close_price
            unrealized = market_value - cost
            unrealized_pct = unrealized / cost if cost > _EPS else None
        else:
            market_value = None
            unrealized = None
            unrealized_pct = None

        cash_yield = (
            ttm_dividends / market_value
            if market_value not in (None, 0.0)
            else None
        )
        cost_yield = dividends_total / cost if cost > _EPS else None

        out.append(
            StockPnlSummaryRead(
                stock_id=h.stock_id,
                stock_code=h.stock_code,
                stock_name=h.stock_name,
                shares=round(shares, 6),
                cost=round(cost, 2),
                market_value=round(market_value, 2) if market_value is not None else None,
                realized=round(realized, 2),
                dividends_total=round(dividends_total, 2),
                unrealized=round(unrealized, 2) if unrealized is not None else None,
                unrealized_pct=round(unrealized_pct, 6) if unrealized_pct is not None else None,
                cash_yield=round(cash_yield, 6) if cash_yield is not None else None,
                cost_yield=round(cost_yield, 6) if cost_yield is not None else None,
                fx_code=_holding_fx_code(session, rows),
                close_price=close_price,
                price_date=price_date,
            )
        )
    return out
