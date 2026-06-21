"""Service-layer tests for import_service."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from sqlmodel import Session, select

import app.services.import_service as svc
from app.models.dashboard.fx_rate import FXRate
from app.models.dashboard.stock_price_history import StockPriceHistory
from app.models.assets.stock import StockJournal
from app.models.monthly_report.journal import Journal


# ---------- Config loaders ----------


def test_load_config_files_missing_tolerated(tmp_path: Path) -> None:
    assert svc.load_invoice_skip_list(str(tmp_path / "missing.json")) == []
    assert svc.load_merchant_mapping(str(tmp_path / "missing.json")) == {}


def test_load_config_files_invalid_json(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("not json", encoding="utf-8")
    assert svc.load_invoice_skip_list(str(bad)) == []
    assert svc.load_merchant_mapping(str(bad)) == {}


def test_load_config_files_happy(tmp_path: Path) -> None:
    skip = tmp_path / "skip.json"
    skip.write_text('["A", "B"]', encoding="utf-8")
    assert svc.load_invoice_skip_list(str(skip)) == ["A", "B"]

    mapping = tmp_path / "map.json"
    mapping.write_text('{"foo": "bar"}', encoding="utf-8")
    assert svc.load_merchant_mapping(str(mapping)) == {"foo": "bar"}


# ---------- Period helpers ----------


def test_period_to_last_day_known_month() -> None:
    assert svc._period_to_last_day("202602") == "20260228"
    assert svc._period_to_last_day("202601") == "20260131"


def test_period_to_last_day_empty_uses_today() -> None:
    out = svc._period_to_last_day("")
    assert len(out) == 8 and out.isdigit()


def test_yfinance_ticker_heuristic() -> None:
    assert svc._yfinance_ticker("2330") == "2330.TW"
    assert svc._yfinance_ticker("AAPL") == "AAPL"


def test_period_to_range_spans_month() -> None:
    # end is the first of the next month (yfinance treats end as exclusive).
    assert svc._period_to_range("202601") == ("2026-01-01", "2026-02-01")
    assert svc._period_to_range("202612") == ("2026-12-01", "2027-01-01")


def test_last_completed_month_is_six_digit_yyyymm() -> None:
    out = svc._last_completed_month()
    assert len(out) == 6 and out.isdigit()


# ---------- Stock price import ----------


class _FakeRow(dict):
    def __getitem__(self, key):
        return super().__getitem__(key)

    def __contains__(self, key) -> bool:
        return super().__contains__(key)


class _FakeFrame:
    def __init__(self, rows: list[dict]):
        self._rows = rows

    def __len__(self):
        return len(self._rows)

    @property
    def iloc(self):
        rows = self._rows

        class _Iloc:
            def __getitem__(self, idx):
                return _FakeRow(rows[idx])

        return _Iloc()


def _patch_yfinance(monkeypatch, frame):
    class _Yf:
        @staticmethod
        def download(*args, **kwargs):
            return frame

    monkeypatch.setitem(__import__("sys").modules, "yfinance", _Yf)


def _patch_yfinance_capture(monkeypatch, frame) -> dict:
    """Like :func:`_patch_yfinance` but records the last ``download()`` call args."""
    calls: dict = {}

    class _Yf:
        @staticmethod
        def download(*args, **kwargs):
            calls["args"] = args
            calls["kwargs"] = kwargs
            return frame

    monkeypatch.setitem(__import__("sys").modules, "yfinance", _Yf)
    return calls


def test_import_stock_prices_upserts_and_skips_duplicates(
    session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    session.add(
        StockJournal(
            stock_id="STK1",
            stock_code="AAPL",
            stock_name="Apple",
            asset_id="AS1",
            expected_spend=0.0,
        )
    )
    session.commit()

    frame = _FakeFrame(
        [{"Open": 100.0, "High": 105.0, "Low": 95.0, "Close": 102.0}]
    )
    _patch_yfinance(monkeypatch, frame)

    # Worker creates its own session(engine); patch the engine to ours.
    engine = session.get_bind()
    monkeypatch.setattr(svc, "engine", engine)

    svc.import_stock_prices("202601")
    fetch_date = svc._period_to_last_day("202601")
    rows = session.exec(
        select(StockPriceHistory).where(StockPriceHistory.stock_code == "AAPL")
    ).all()
    assert len(rows) == 1
    assert rows[0].close_price == 102.0
    assert rows[0].fetch_date == fetch_date

    # Re-run with new prices: idempotent upsert (still 1 row, updated values).
    frame2 = _FakeFrame(
        [{"Open": 110.0, "High": 115.0, "Low": 105.0, "Close": 112.0}]
    )
    _patch_yfinance(monkeypatch, frame2)
    svc.import_stock_prices("202601")
    session.expire_all()
    rows = session.exec(
        select(StockPriceHistory).where(StockPriceHistory.stock_code == "AAPL")
    ).all()
    assert len(rows) == 1
    assert rows[0].close_price == 112.0


def test_import_stock_prices_fetches_month_history(
    session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A period fetches that month's range; the last bar is stored at month-end."""
    session.add(
        StockJournal(
            stock_id="STK1", stock_code="AAPL", stock_name="Apple",
            asset_id="AS1", expected_spend=0.0,
        )
    )
    session.commit()

    frame = _FakeFrame([{"Open": 90.0, "High": 95.0, "Low": 88.0, "Close": 93.0}])
    calls = _patch_yfinance_capture(monkeypatch, frame)
    monkeypatch.setattr(svc, "engine", session.get_bind())

    svc.import_stock_prices("202601")

    # Historical window, not period="1d".
    assert calls["kwargs"].get("start") == "2026-01-01"
    assert calls["kwargs"].get("end") == "2026-02-01"
    assert "period" not in calls["kwargs"]

    row = session.exec(
        select(StockPriceHistory).where(StockPriceHistory.stock_code == "AAPL")
    ).first()
    assert row is not None
    assert row.fetch_date == "20260131"
    assert row.close_price == 93.0


def test_import_stock_prices_empty_period_uses_latest(
    session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    session.add(
        StockJournal(
            stock_id="STK1", stock_code="AAPL", stock_name="Apple",
            asset_id="AS1", expected_spend=0.0,
        )
    )
    session.commit()

    frame = _FakeFrame([{"Open": 1.0, "High": 1.0, "Low": 1.0, "Close": 7.0}])
    calls = _patch_yfinance_capture(monkeypatch, frame)
    monkeypatch.setattr(svc, "engine", session.get_bind())

    svc.import_stock_prices("")

    assert calls["kwargs"].get("period") == "1d"
    assert "start" not in calls["kwargs"]
    row = session.exec(
        select(StockPriceHistory).where(StockPriceHistory.stock_code == "AAPL")
    ).first()
    assert row is not None
    assert row.fetch_date == svc._period_to_last_day("")


# ---------- FX rate import ----------


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


class _FakeClient:
    def __init__(self, payload):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def get(self, url):
        return _FakeResponse(self._payload)


def test_import_fx_rates_idempotent(
    session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = {
        "SubInfo": [
            {"DataValue4": "USD", "DataValue2": "31.50"},
            {"DataValue4": "JPY", "DataValue2": "0.21"},
            {"DataValue4": "BAD", "DataValue2": ""},
        ]
    }
    import httpx

    monkeypatch.setattr(httpx, "Client", lambda **kw: _FakeClient(payload))

    engine = session.get_bind()
    monkeypatch.setattr(svc, "engine", engine)

    svc.import_fx_rates("202601")
    rows = session.exec(select(FXRate)).all()
    assert {(r.code, r.buy_rate) for r in rows} == {("USD", 31.5), ("JPY", 0.21)}

    # Re-run; counts unchanged.
    svc.import_fx_rates("202601")
    rows = session.exec(select(FXRate)).all()
    assert len(rows) == 2


def test_import_fx_rates_current_month_uses_today(
    session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Importing the ongoing month stores today's real date, not a fake month-end."""
    today = date.today()
    payload = {"SubInfo": [{"DataValue4": "USD", "DataValue2": "31.50"}]}
    import httpx

    monkeypatch.setattr(httpx, "Client", lambda **kw: _FakeClient(payload))
    monkeypatch.setattr(svc, "engine", session.get_bind())

    svc.import_fx_rates(today.strftime("%Y%m"))
    rows = session.exec(select(FXRate)).all()
    assert len(rows) == 1
    assert rows[0].import_date == today.strftime("%Y%m%d")


def test_import_fx_rates_past_month_clamps_to_month_end(
    session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A past period still clamps to that month-end (Sinopac has no history)."""
    payload = {"SubInfo": [{"DataValue4": "USD", "DataValue2": "30.00"}]}
    import httpx

    monkeypatch.setattr(httpx, "Client", lambda **kw: _FakeClient(payload))
    monkeypatch.setattr(svc, "engine", session.get_bind())

    svc.import_fx_rates("202001")  # safely in the past relative to any test run
    rows = session.exec(select(FXRate)).all()
    assert len(rows) == 1
    assert rows[0].import_date == "20200131"


def test_fx_upsert_is_idempotent(session: Session) -> None:
    svc._upsert_fx(session, "20260131", "USD", 31.5)
    session.commit()
    svc._upsert_fx(session, "20260131", "USD", 31.6)
    session.commit()
    rows = session.exec(select(FXRate)).all()
    assert len(rows) == 1
    assert rows[0].buy_rate == 31.6


# ---------- Startup catch-up ----------


def test_catch_up_fx_stores_today_then_skips(
    session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = {"SubInfo": [{"DataValue4": "USD", "DataValue2": "31.50"}]}
    import httpx

    monkeypatch.setattr(httpx, "Client", lambda **kw: _FakeClient(payload))
    monkeypatch.setattr(svc, "engine", session.get_bind())

    svc._catch_up_fx()

    today = date.today().strftime("%Y%m%d")
    rows = session.exec(select(FXRate)).all()
    assert len(rows) == 1
    assert rows[0].import_date == today  # true date, not a month-end relabel
    assert rows[0].buy_rate == 31.5

    # Second run the same day: today's row already exists → no fetch.
    calls = {"n": 0}
    real = svc._fetch_and_store_fx

    def _spy(import_date: str) -> None:
        calls["n"] += 1
        real(import_date)

    monkeypatch.setattr(svc, "_fetch_and_store_fx", _spy)
    svc._catch_up_fx()
    assert calls["n"] == 0
    assert len(session.exec(select(FXRate)).all()) == 1


def test_catch_up_stock_only_fetches_missing(
    session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    period = svc._last_completed_month()
    fetch_date = svc._period_to_last_day(period)
    for code in ("AAPL", "MSFT"):
        session.add(
            StockJournal(
                stock_id=f"STK-{code}", stock_code=code, stock_name=code,
                asset_id="AS1", expected_spend=0.0,
            )
        )
    # AAPL already has last month's row → it must be left untouched.
    session.add(
        StockPriceHistory(
            stock_code="AAPL", fetch_date=fetch_date,
            open_price=10.0, highest_price=10.0, lowest_price=10.0, close_price=10.0,
        )
    )
    session.commit()

    frame = _FakeFrame([{"Open": 50.0, "High": 50.0, "Low": 50.0, "Close": 50.0}])
    _patch_yfinance_capture(monkeypatch, frame)
    monkeypatch.setattr(svc, "engine", session.get_bind())

    svc._catch_up_stock()
    session.expire_all()

    aapl = session.exec(
        select(StockPriceHistory).where(
            StockPriceHistory.stock_code == "AAPL",
            StockPriceHistory.fetch_date == fetch_date,
        )
    ).first()
    assert aapl is not None and aapl.close_price == 10.0  # untouched

    msft = session.exec(
        select(StockPriceHistory).where(
            StockPriceHistory.stock_code == "MSFT",
            StockPriceHistory.fetch_date == fetch_date,
        )
    ).first()
    assert msft is not None and msft.close_price == 50.0  # freshly fetched


def test_startup_catch_up_runs_steps_in_order(monkeypatch: pytest.MonkeyPatch) -> None:
    ran: list[str] = []
    monkeypatch.setattr(svc, "_catch_up_fx", lambda: ran.append("fx"))
    monkeypatch.setattr(svc, "_catch_up_fx_history", lambda: ran.append("fx_history"))
    monkeypatch.setattr(svc, "_catch_up_stock", lambda: ran.append("stock"))
    svc.startup_catch_up()
    assert ran == ["fx", "fx_history", "stock"]


def test_startup_catch_up_never_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom() -> None:
        raise RuntimeError("network down")

    monkeypatch.setattr(svc, "_catch_up_fx", _boom)
    monkeypatch.setattr(svc, "_catch_up_fx_history", _boom)
    monkeypatch.setattr(svc, "_catch_up_stock", _boom)
    svc.startup_catch_up()  # must swallow all three and not propagate


# ---------- Bank of Taiwan historical FX backfill ----------


class _FakeCsvResponse:
    def __init__(self, text: str):
        self._text = text

    @property
    def text(self) -> str:
        return self._text

    def raise_for_status(self) -> None:
        pass


class _FakeCsvClient:
    def __init__(self, text: str):
        self._text = text

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def get(self, url):
        return _FakeCsvResponse(self._text)


def test_fetch_bot_spot_buy_picks_nearest_on_or_before_month_end(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Newest-first rows; spot-buy (即期買入) is column index 4.
    csv_text = (
        "\r\n".join(
            [
                "資料日期,幣別,匯率,現金,即期",       # header → skipped (col0 not a date)
                "20260502,USD,本行買入,31.00,31.50",   # after 2026-04-30 → skipped
                "20260430,USD,本行買入,31.10,31.61",   # month-end → picked
                "20260429,USD,本行買入,31.12,31.63",
            ]
        )
        + "\r\n"
    )
    import httpx

    monkeypatch.setattr(httpx, "Client", lambda **kw: _FakeCsvClient(csv_text))
    assert svc._fetch_bot_spot_buy_at_month_end("USD", "202604") == ("20260430", 31.61)


def test_fetch_bot_spot_buy_none_when_all_after_month_end(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    csv_text = "資料日期,幣別,匯率,現金,即期\r\n20260502,USD,本行買入,31.0,31.5\r\n"
    import httpx

    monkeypatch.setattr(httpx, "Client", lambda **kw: _FakeCsvClient(csv_text))
    assert svc._fetch_bot_spot_buy_at_month_end("USD", "202604") is None


def test_catch_up_fx_history_backfills_only_missing(
    session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    period = svc._last_completed_month()
    month_end = svc._period_to_last_day(period)
    # USD: only an old prior-month row → MISSING inside `period`.
    # JPY: a row inside `period` → PRESENT, must be left to Sinopac.
    session.add(FXRate(import_date="20200131", code="USD", buy_rate=30.0))
    session.add(FXRate(import_date=f"{period}10", code="JPY", buy_rate=0.21))
    session.commit()
    monkeypatch.setattr(svc, "engine", session.get_bind())

    calls: list[tuple[str, str]] = []

    def _fake_bot(ccy: str, per: str):
        calls.append((ccy, per))
        return svc._period_to_last_day(per), 31.9

    monkeypatch.setattr(svc, "_fetch_bot_spot_buy_at_month_end", _fake_bot)

    svc._catch_up_fx_history()
    session.expire_all()

    # USD backfilled at BOT's returned month-end date; JPY untouched (no call).
    usd = session.exec(
        select(FXRate).where(FXRate.code == "USD", FXRate.import_date == month_end)
    ).first()
    assert usd is not None and usd.buy_rate == 31.9
    assert calls == [("USD", period)]


# ---------- Invoice CSV import ----------


def _invoice_csv(rows: list[list[str]]) -> str:
    return "\n".join("|".join(r) for r in rows) + "\n"


def _configure_invoice_paths(monkeypatch, skip_path, map_path, log_path):
    # Patch the settings object that import_service holds a reference to.
    live = svc.settings

    monkeypatch.setattr(live, "invoice_skip_path", str(skip_path))
    monkeypatch.setattr(live, "merchant_mapping_path", str(map_path))
    monkeypatch.setattr(live, "invoice_error_log", str(log_path))


def test_import_invoices_partial_success_and_dedup(
    session: Session, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    skip_path = tmp_path / "skip.json"
    map_path = tmp_path / "map.json"
    log_path = tmp_path / "logs" / "errors.log"
    skip_path.write_text('["SKIPME"]', encoding="utf-8")
    map_path.write_text('{"Coffee": "FOOD-01"}', encoding="utf-8")
    _configure_invoice_paths(monkeypatch, skip_path, map_path, log_path)

    engine = session.get_bind()
    monkeypatch.setattr(svc, "engine", engine)

    rows = [
        # (M, carrier_name, carrier_no, invoice_date, shop_id, shop_name, invoice_number, total)
        ["M", "Carrier", "CAR1", "20260105", "S1", "Coffee Shop", "INV-1", "150", "OK", ""],
        ["D", "INV-1", "150", "Latte", ""],
        # malformed (amount) → failed
        ["M", "Carrier", "CAR1", "20260106", "S1", "Bad Shop", "INV-2", "abc", "OK", ""],
        # in skip-list → skipped
        ["M", "Carrier", "SKIPME", "20260107", "S1", "Skipped", "INV-3", "100", "OK", ""],
        # a different month — now imported too, since the period filter is gone
        ["M", "Carrier", "CAR1", "20260205", "S1", "Other", "INV-4", "200", "OK", ""],
    ]
    content = _invoice_csv(rows)

    result = svc.import_invoices(content)
    assert result.imported == 2  # INV-1 + INV-4
    assert result.skipped == 1  # SKIPME
    assert result.failed == 1  # INV-2 bad amount
    assert any(e.line == 3 for e in result.errors)

    # Per-month breakdown: INV-1 imported + INV-3 skip-list in 202601, INV-4 in
    # 202602. INV-2 failed before vesting_month was derived, so it's omitted.
    months = {m.month: m for m in result.months}
    assert set(months) == {"202601", "202602"}
    assert (months["202601"].imported, months["202601"].skipped) == (1, 1)
    assert (months["202602"].imported, months["202602"].skipped) == (1, 0)

    # Re-run: previously-imported INV-1 + INV-4 now dedup → skipped goes up.
    result2 = svc.import_invoices(content)
    assert result2.imported == 0
    assert result2.skipped == 3  # INV-1 dedup + INV-4 dedup + SKIPME
    months2 = {m.month: m for m in result2.months}
    assert (months2["202601"].imported, months2["202601"].skipped) == (0, 2)
    assert (months2["202602"].imported, months2["202602"].skipped) == (0, 1)

    journals = session.exec(select(Journal)).all()
    assert len(journals) == 2
    inv1 = next(j for j in journals if j.invoice_number == "INV-1")
    assert inv1.action_main == "FOOD-01"
    assert "Latte" in (inv1.note or "")


def test_import_invoices_empty_content(
    session: Session, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    skip_path = tmp_path / "skip.json"
    map_path = tmp_path / "map.json"
    log_path = tmp_path / "logs" / "errors.log"
    skip_path.write_text("[]", encoding="utf-8")
    map_path.write_text("{}", encoding="utf-8")
    _configure_invoice_paths(monkeypatch, skip_path, map_path, log_path)

    engine = session.get_bind()
    monkeypatch.setattr(svc, "engine", engine)

    result = svc.import_invoices("")
    assert result.imported == 0
    assert result.skipped == 0
    assert result.failed == 0
    assert result.months == []
    assert result.errors == []


def test_invoice_dedup_and_partial_success(
    session: Session, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Alias for the granular spec's named assertion (spec sub-task 9)."""
    test_import_invoices_partial_success_and_dedup(session, monkeypatch, tmp_path)
