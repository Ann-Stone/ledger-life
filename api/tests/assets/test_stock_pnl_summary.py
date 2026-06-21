"""Tests for per-stock P&L summary (asset-management columns).

``excute_price`` is the whole-transaction cash amount (fees included), not a
per-share price. Covers moving-average cost, realized capital gains, fees raising
cost / lowering realized, stock-dividend cost dilution, cash-dividend yields
(cumulative + trailing-12m), FX/own-currency passthrough, the no-price and
fully-sold edge cases, and the router.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.assets.stock import StockDetailCreate, StockJournalCreate
from app.models.dashboard.stock_price_history import StockPriceHistory
from app.models.settings.account import Account
from app.services.asset_service import create_stock, create_stock_detail
from app.services.stock_service import compute_stock_pnl_summary

AS_OF = "202606"
ASSET = "AC-STK-001"


# ---------- builders ----------


def _holding(session: Session, stock_id: str, code: str = "2330", asset_id: str = ASSET) -> None:
    create_stock(
        session,
        StockJournalCreate(
            stock_id=stock_id,
            stock_code=code,
            stock_name=code,
            asset_id=asset_id,
            expected_spend=0.0,
        ),
    )


def _detail(
    session: Session,
    stock_id: str,
    excute_type: str,
    amount: float,
    total: float,  # whole-transaction cash amount (fees included), not per-share
    date: str,
    account_id: str = "TWD-ACC",
) -> None:
    create_stock_detail(
        session,
        stock_id,
        StockDetailCreate(
            stock_id=stock_id,
            excute_type=excute_type,
            excute_amount=amount,
            excute_price=total,
            excute_date=date,
            account_id=account_id,
            account_name=account_id,
        ),
    )


def _add_price(session: Session, code: str, date: str, close: float) -> None:
    session.add(
        StockPriceHistory(
            stock_code=code,
            fetch_date=date,
            open_price=close,
            highest_price=close,
            lowest_price=close,
            close_price=close,
        )
    )
    session.commit()


def _add_account(session: Session, account_id: str, fx_code: str) -> None:
    session.add(
        Account(
            account_id=account_id,
            name=account_id,
            account_type="bank",
            fx_code=fx_code,
            is_calculate="Y",
            in_use="Y",
            discount=1.0,
            owner="stone",
            account_index=1,
        )
    )
    session.commit()


def _summary(session: Session, stock_id: str, as_of: str = AS_OF):
    rows = compute_stock_pnl_summary(session, asset_id=ASSET, as_of_month=as_of)
    return next(s for s in rows if s.stock_id == stock_id)


# ---------- cost basis + realized ----------


def test_moving_average_partial_sell(session: Session):
    """buy 100 (5000), buy 100 (6000) → avg 55; sell 50 for 3500 → realized 750."""
    _holding(session, "H1")
    _detail(session, "H1", "buy", 100, 5000, "20260101")
    _detail(session, "H1", "buy", 100, 6000, "20260201")
    _detail(session, "H1", "sell", 50, 3500, "20260301")  # 50 sold, net proceeds 3500
    _add_price(session, "2330", "20260620", 80.0)

    s = _summary(session, "H1")
    assert s.shares == 150
    assert s.cost == 8250.0           # 150 × avg 55
    assert s.realized == 750.0        # 3500 − 50 × 55
    assert s.market_value == 12000.0  # 150 × 80 (close is a per-share quote)
    assert s.unrealized == 3750.0     # 12000 − 8250
    assert s.unrealized_pct == pytest.approx(3750 / 8250, abs=1e-6)


def test_fees_raise_cost_and_lower_realized(session: Session):
    """The total-amount convention folds fees into cost basis and realized."""
    _holding(session, "H1")
    _detail(session, "H1", "buy", 100, 5100, "20260101")  # 5000 + 100 buy fee → avg 51
    _detail(session, "H1", "sell", 50, 3450, "20260301")  # 3500 − 50 sell fee, net 3450
    _add_price(session, "2330", "20260620", 60.0)

    s = _summary(session, "H1")
    assert s.shares == 50
    assert s.cost == 2550.0       # 50 × avg 51 (buy fee in basis)
    assert s.realized == 900.0    # 3450 − 50 × 51 (both fees reduce the gain)
    assert s.market_value == 3000.0


def test_sell_does_not_change_remaining_average(session: Session):
    """A later buy after a sell uses the unchanged post-sell average."""
    _holding(session, "H1")
    _detail(session, "H1", "buy", 100, 5000, "20260101")  # avg 50
    _detail(session, "H1", "sell", 40, 3600, "20260201")  # realized 3600−2000=1600, avg still 50
    _add_price(session, "2330", "20260620", 50.0)

    s = _summary(session, "H1")
    assert s.shares == 60
    assert s.cost == 3000.0          # 60 × 50
    assert s.realized == 1600.0
    assert s.unrealized == 0.0       # 60 × 50 − 3000


def test_fully_sold_is_flat(session: Session):
    """Fully exiting zeroes cost/market value; pct & cost_yield undefined."""
    _holding(session, "H1")
    _detail(session, "H1", "buy", 100, 5000, "20260101")
    _detail(session, "H1", "sell", 100, 7000, "20260301")
    _add_price(session, "2330", "20260620", 80.0)

    s = _summary(session, "H1")
    assert s.shares == 0
    assert s.cost == 0.0
    assert s.realized == 2000.0       # 7000 − 5000
    assert s.market_value == 0.0
    assert s.unrealized == 0.0
    assert s.unrealized_pct is None
    assert s.cost_yield is None


# ---------- stock dividend ----------


def test_stock_dividend_dilutes_average(session: Session):
    """Stock dividend adds shares without cost → average drops."""
    _holding(session, "H1")
    _detail(session, "H1", "buy", 100, 5000, "20260101")  # cost 5000
    _detail(session, "H1", "stock", 10, 0, "20260201")    # +10 shares, cost flat
    _add_price(session, "2330", "20260620", 50.0)

    s = _summary(session, "H1")
    assert s.shares == 110
    assert s.cost == 5000.0
    assert s.market_value == 5500.0          # 110 × 50
    assert s.unrealized == 500.0             # gain purely from the bonus shares


# ---------- cash dividend + yields ----------


def test_cash_dividend_feeds_both_yields(session: Session):
    """A cash row's total dividend drives cost_yield and (in-window) cash_yield."""
    _holding(session, "H1")
    _detail(session, "H1", "buy", 100, 5000, "20260101")  # cost 5000
    _detail(session, "H1", "cash", 0, 200, "20260315")    # dividend total 200, within ttm
    _add_price(session, "2330", "20260620", 50.0)

    s = _summary(session, "H1")
    assert s.dividends_total == 200.0
    assert s.market_value == 5000.0
    assert s.cost_yield == pytest.approx(200 / 5000, abs=1e-6)   # 0.04
    assert s.cash_yield == pytest.approx(200 / 5000, abs=1e-6)   # ttm / market value


def test_ttm_window_excludes_old_dividends(session: Session):
    """Dividends older than 12 months count toward cost_yield but not cash_yield."""
    _holding(session, "H1")
    _detail(session, "H1", "buy", 100, 5000, "20240101")
    _detail(session, "H1", "cash", 0, 300, "20240601")   # before ttm cutoff
    _detail(session, "H1", "cash", 0, 200, "20260315")   # within ttm
    _add_price(session, "2330", "20260620", 50.0)

    s = _summary(session, "H1")
    assert s.dividends_total == 500.0
    assert s.cost_yield == pytest.approx(500 / 5000, abs=1e-6)   # cumulative
    assert s.cash_yield == pytest.approx(200 / 5000, abs=1e-6)   # ttm only


# ---------- currency + no-price ----------


def test_fx_code_from_settling_account(session: Session):
    """Figures report in the holding's own currency (settling account fx_code)."""
    _add_account(session, "USD-ACC", "USD")
    _holding(session, "H1", code="VOO")
    _detail(session, "H1", "buy", 5, 2400, "20260120", account_id="USD-ACC")  # 5 × $480
    _add_price(session, "VOO", "20260620", 500.0)

    s = _summary(session, "H1")
    assert s.fx_code == "USD"
    assert s.cost == 2400.0
    assert s.market_value == 2500.0


def test_fx_code_defaults_to_base_currency(session: Session):
    _holding(session, "H1")
    _detail(session, "H1", "buy", 10, 1000, "20260101")  # account not seeded
    s = _summary(session, "H1")
    assert s.fx_code == "TWD"


def test_no_price_leaves_market_value_null(session: Session):
    """No StockPriceHistory row → market value / unrealized are null, cost stands."""
    _holding(session, "H1")
    _detail(session, "H1", "buy", 100, 5000, "20260101")

    s = _summary(session, "H1")
    assert s.cost == 5000.0
    assert s.market_value is None
    assert s.unrealized is None
    assert s.unrealized_pct is None
    assert s.cash_yield is None


def test_as_of_month_ignores_future_transactions(session: Session):
    """A buy dated after as_of_month is excluded from the snapshot."""
    _holding(session, "H1")
    _detail(session, "H1", "buy", 100, 5000, "20260101")
    _detail(session, "H1", "buy", 100, 6000, "20260701")  # after AS_OF (202606)
    _add_price(session, "2330", "20260620", 50.0)

    s = _summary(session, "H1")
    assert s.shares == 100
    assert s.cost == 5000.0


# ---------- router ----------


def test_summary_endpoint_happy(client: TestClient, session: Session):
    _holding(session, "H1")
    _detail(session, "H1", "buy", 100, 5000, "20260101")
    _add_price(session, "2330", "20260620", 60.0)

    resp = client.get(
        "/assets/stocks/summary", params={"asset_id": ASSET, "as_of_month": AS_OF}
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == 1
    assert len(body["data"]) == 1
    row = body["data"][0]
    assert row["stock_id"] == "H1"
    assert row["cost"] == 5000.0
    assert row["market_value"] == 6000.0
    assert row["unrealized"] == 1000.0


def test_summary_endpoint_requires_asset_id(client: TestClient):
    resp = client.get("/assets/stocks/summary")
    assert resp.status_code == 422
