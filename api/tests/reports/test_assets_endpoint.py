"""BE-025 — asset breakdown endpoint tests."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.monthly_report.account_balance import AccountBalance
from app.models.monthly_report.estate_net_value_history import EstateNetValueHistory
from app.models.monthly_report.stock_net_value_history import StockNetValueHistory


def test_get_asset_breakdown_happy(client: TestClient) -> None:
    r = client.get("/reports/assets")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 0.0
    types = {item["type"] for item in data["items"]}
    assert types == {"accounts", "stocks", "estates", "insurances", "other"}


def test_get_asset_breakdown_golden(client: TestClient, session: Session) -> None:
    session.add(
        AccountBalance(
            vesting_month="202604",
            id="A1",
            name="TWD Bank",
            balance=100000.0,
            fx_code="TWD",
            fx_rate=1.0,
            is_calculate="Y",
        )
    )
    session.add(
        StockNetValueHistory(
            vesting_month="202604",
            id="S1",
            asset_id="AC1",
            stock_code="AAPL",
            stock_name="Apple",
            amount=10.0,
            price=2000.0,
            cost=1500.0,
            fx_code="USD",
            fx_rate=30.0,
        )
    )
    session.add(
        EstateNetValueHistory(
            vesting_month="202604",
            id="E1",
            asset_id="AC2",
            name="Condo",
            market_value=200000.0,
            cost=0.0,
            estate_status="hold",
            fx_code="TWD",
            fx_rate=1.0,
        )
    )
    session.commit()

    r = client.get("/reports/assets")
    data = r.json()["data"]
    # 100000 + 60000 + 200000 = 360000
    assert data["total"] == 360000.0
    by_type = {item["type"]: item for item in data["items"]}
    assert by_type["accounts"]["amount"] == 100000.0
    assert by_type["stocks"]["amount"] == 60000.0
    assert by_type["estates"]["amount"] == 200000.0
    assert abs(sum(item["share"] for item in data["items"]) - 100.0) < 0.05
