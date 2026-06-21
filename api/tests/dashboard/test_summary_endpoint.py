"""BE-026 — summary endpoint tests."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.monthly_report.account_balance import AccountBalance
from app.models.monthly_report.journal import Journal
from app.models.monthly_report.loan_balance import LoanBalance
from app.models.settings.code_data import CodeData


def _journal(**kw) -> Journal:
    base = dict(
        spend_way="A1",
        spend_way_type="account",
        spend_way_table="Account",
        action_main="X01",
        action_main_type="Floating",
        action_main_table="Code_Data",
        spending=-100.0,
        spend_date="20230110",
        vesting_month="202301",
    )
    base.update(kw)
    return Journal(**base)


def test_get_summary_spending_happy(client: TestClient, session: Session) -> None:
    session.add(_journal(vesting_month="202301", spending=-100.0))
    session.commit()

    r = client.get("/dashboard/summary?type=spending&period=202301-202301")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["type"] == "spending"
    assert data["points"][0]["value"] == 100.0


def test_get_summary_spending_golden(client: TestClient, session: Session) -> None:
    for m, amt in [("202301", -100.0), ("202302", -200.0), ("202303", -300.0)]:
        session.add(_journal(vesting_month=m, spending=amt))
    session.commit()

    r = client.get("/dashboard/summary?type=spending&period=202301-202303")
    data = r.json()["data"]
    by_period = {p["period"]: p["value"] for p in data["points"]}
    assert by_period == {"202301": 100.0, "202302": 200.0, "202303": 300.0}


def test_get_summary_freedom_ratio_golden(client: TestClient, session: Session) -> None:
    session.add(CodeData(code_id="F01", code_type="Fixed", name="Rent", in_use="Y", code_index=1))
    session.add(_journal(vesting_month="202301", action_main_type="Income", spending=10000.0))
    session.add(
        _journal(
            vesting_month="202301",
            action_main="F01",
            action_main_type="Fixed",
            spending=-2500.0,
        )
    )
    session.commit()

    r = client.get("/dashboard/summary?type=freedom_ratio&period=202301-202301")
    data = r.json()["data"]
    point = data["points"][0]
    assert point["value"] == 0.75
    assert point["breakdown"] == {"income": 10000.0, "fixed_expenses": 2500.0}
    recomputed = (
        point["breakdown"]["income"] - point["breakdown"]["fixed_expenses"]
    ) / point["breakdown"]["income"]
    assert point["value"] == pytest.approx(recomputed, abs=1e-4)


def test_get_summary_asset_debt_trend_golden(client: TestClient, session: Session) -> None:
    session.add(
        AccountBalance(
            vesting_month="202301",
            id="A1",
            name="Bank",
            balance=100000.0,
            fx_code="TWD",
            fx_rate=1.0,
            is_calculate="Y",
        )
    )
    session.add(LoanBalance(vesting_month="202301", id="L1", name="Loan", balance=-30000.0, cost=0.0, fx_code="TWD", fx_rate=1.0))
    session.commit()

    r = client.get("/dashboard/summary?type=asset_debt_trend&period=202301-202302")
    data = r.json()["data"]
    by_period = {p["period"]: p["value"] for p in data["points"]}
    assert by_period["202301"] == 70000.0
    assert by_period["202302"] == 70000.0

    expected_keys = {"accounts", "stocks", "estates", "insurances", "loans", "cards"}
    for p in data["points"]:
        assert p["breakdown"] is not None
        assert set(p["breakdown"].keys()) == expected_keys
        assert sum(p["breakdown"].values()) == pytest.approx(p["value"], abs=0.01)
        assert p["breakdown"]["loans"] <= 0
        assert p["breakdown"]["cards"] <= 0


def test_get_summary_spending_breakdown_is_null(
    client: TestClient, session: Session
) -> None:
    """spending variant must continue to return breakdown=null in JSON."""
    session.add(_journal(vesting_month="202301", spending=-100.0))
    session.commit()
    r = client.get("/dashboard/summary?type=spending&period=202301-202301")
    assert r.status_code == 200
    for p in r.json()["data"]["points"]:
        assert p["breakdown"] is None


def test_get_summary_invalid_period_returns_422(client: TestClient) -> None:
    r = client.get("/dashboard/summary?type=spending&period=2023-2024")
    assert r.status_code == 422
