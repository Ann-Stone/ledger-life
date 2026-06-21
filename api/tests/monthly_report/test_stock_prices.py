"""BE-018 — Stock price management tests."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.assets.stock import StockJournal
from app.models.dashboard.stock_price_history import StockPriceHistory
from app.models.monthly_report.stock_price import (
    StockPriceCreate,
    StockPriceMonthRead,
    StockPriceRead,
)
from app.services.stock_service import (
    fetch_yfinance_price,
    insert_stock_price,
    list_month_stock_prices,
    select_in_month_close_price,
    select_month_close_price,
)


def _price(**ov) -> StockPriceHistory:
    base = dict(
        stock_code="AAPL",
        fetch_date="20260301",
        open_price=180.0,
        highest_price=185.0,
        lowest_price=178.0,
        close_price=182.0,
    )
    base.update(ov)
    return StockPriceHistory(**base)


def test_stock_price_schemas() -> None:
    for cls in (StockPriceCreate, StockPriceRead, StockPriceMonthRead):
        js = cls.model_json_schema()
        assert "example" in js, cls.__name__
        for n, p in js["properties"].items():
            assert "description" in p, f"{cls.__name__}.{n}"
            assert "examples" in p, f"{cls.__name__}.{n}"


def test_select_month_close_price_fallback(session: Session) -> None:
    session.add(_price(fetch_date="20260120", close_price=170.0))
    session.add(_price(fetch_date="20260315", close_price=190.0))
    session.add(_price(fetch_date="20260410", close_price=200.0))
    session.commit()

    # March: pick the in-month row.
    march = select_month_close_price(session, "AAPL", "202603")
    assert march is not None and march.close_price == 190.0

    # February: fall back to most recent prior row.
    feb = select_month_close_price(session, "AAPL", "202602")
    assert feb is not None and feb.close_price == 170.0

    # Unknown ticker.
    assert select_month_close_price(session, "MSFT", "202603") is None


def test_select_in_month_close_price_no_fallback(session: Session) -> None:
    session.add(_price(fetch_date="20260120", close_price=170.0))
    session.add(_price(fetch_date="20260315", close_price=190.0))
    session.commit()

    # March has an in-month row.
    march = select_in_month_close_price(session, "AAPL", "202603")
    assert march is not None and march.close_price == 190.0

    # February has none → no fallback to January's row.
    assert select_in_month_close_price(session, "AAPL", "202602") is None


def test_list_month_stock_prices_golden(session: Session) -> None:
    session.add(StockJournal(stock_id="H1", stock_code="AAPL", stock_name="Apple", asset_id="A", expected_spend=0.0))
    session.add(StockJournal(stock_id="H2", stock_code="GOOG", stock_name="Google", asset_id="A", expected_spend=0.0))
    session.add(_price(stock_code="AAPL", fetch_date="20260331", close_price=200.0))
    # GOOG only has a January row — outside the requested March window.
    session.add(_price(stock_code="GOOG", fetch_date="20260120", close_price=140.0))
    session.commit()

    result = list_month_stock_prices(session, "202603")
    by_code = {r.stock_code: r for r in result}
    # AAPL: in-month row with its date.
    assert by_code["AAPL"].close_price == 200.0
    assert by_code["AAPL"].fetch_date == "20260331"
    # GOOG: no March row → blank, signalling a fetch is needed.
    assert by_code["GOOG"].close_price is None
    assert by_code["GOOG"].fetch_date is None


def test_insert_stock_price_manual(session: Session) -> None:
    payload = StockPriceCreate(
        stock_code="AAPL",
        fetch_date="20260301",
        open_price=180.0,
        highest_price=185.0,
        lowest_price=178.0,
        close_price=182.0,
        trigger_yfinance=False,
    )
    row = insert_stock_price(session, payload)
    assert row.close_price == 182.0
    persisted = session.exec(select(StockPriceHistory)).all()
    assert len(persisted) == 1


def test_insert_stock_price_with_yfinance(session: Session) -> None:
    payload = StockPriceCreate(
        stock_code="AAPL",
        fetch_date="20260301",
        open_price=180.0,
        highest_price=185.0,
        lowest_price=178.0,
        close_price=0.0,
        trigger_yfinance=True,
    )
    with patch("app.services.stock_service.fetch_yfinance_price", return_value=199.99):
        row = insert_stock_price(session, payload)
    assert row.close_price == 199.99


def test_fetch_yfinance_retry() -> None:
    """Force three failures and confirm RuntimeError after exhaustion."""

    class _FakeTicker:
        def __init__(self, *_a, **_kw): pass

        def history(self, *a, **kw):
            raise RuntimeError("boom")

    with patch("yfinance.Ticker", _FakeTicker), patch("time.sleep"):
        with pytest.raises(RuntimeError):
            fetch_yfinance_price("AAPL", "20260301")


def test_get_stock_prices_endpoint(client: TestClient, session: Session) -> None:
    session.add(StockJournal(stock_id="H1", stock_code="AAPL", stock_name="Apple", asset_id="A", expected_spend=0.0))
    session.add(_price(stock_code="AAPL", fetch_date="20260331", close_price=210.0))
    session.commit()

    r = client.get("/monthly-report/stock-prices/202603")
    assert r.status_code == 200
    assert r.json()["data"] == [
        {
            "stock_code": "AAPL",
            "stock_name": "Apple",
            "close_price": 210.0,
            "fetch_date": "20260331",
        }
    ]


def test_post_stock_price_created(client: TestClient) -> None:
    body = {
        "stock_code": "AAPL",
        "fetch_date": "20260301",
        "open_price": 180.0,
        "highest_price": 185.0,
        "lowest_price": 178.0,
        "close_price": 182.0,
        "trigger_yfinance": False,
    }
    r = client.post("/monthly-report/stock-prices", json=body)
    assert r.status_code == 201
    assert r.json()["data"]["close_price"] == 182.0


def test_stock_price_validation_errors(client: TestClient) -> None:
    # Bad vesting_month format → 422
    r = client.get("/monthly-report/stock-prices/2026-03")
    assert r.status_code == 422

    # Missing stock_code on POST → 422
    body = {
        "fetch_date": "20260301",
        "open_price": 180.0,
        "highest_price": 185.0,
        "lowest_price": 178.0,
        "close_price": 182.0,
    }
    r = client.post("/monthly-report/stock-prices", json=body)
    assert r.status_code == 422


def test_post_stock_price_yfinance_502(client: TestClient) -> None:
    body = {
        "stock_code": "AAPL",
        "fetch_date": "20260301",
        "open_price": 180.0,
        "highest_price": 185.0,
        "lowest_price": 178.0,
        "close_price": 0.0,
        "trigger_yfinance": True,
    }
    with patch(
        "app.services.stock_service.fetch_yfinance_price",
        side_effect=RuntimeError("network down"),
    ):
        r = client.post("/monthly-report/stock-prices", json=body)
    assert r.status_code == 502


def test_router_mounted() -> None:
    from app.main import app

    # Use FastAPI's own resolved schema paths rather than walking app.routes:
    # the internal route-tree structure changed across starlette versions, but
    # openapi()["paths"] is the stable, version-agnostic view of mounted paths.
    paths = set(app.openapi()["paths"])
    assert "/monthly-report/stock-prices/{vesting_month}" in paths
    assert "/monthly-report/stock-prices" in paths
