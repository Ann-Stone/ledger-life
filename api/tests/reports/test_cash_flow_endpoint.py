"""Cash-flow statement (現金流量表) endpoint tests."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.assets.loan import LoanJournal
from app.models.monthly_report.journal import Journal


def _journal(**overrides) -> Journal:
    base = dict(
        vesting_month="202603",
        spend_date="20260305",
        spend_way="A1",
        spend_way_type="account",
        spend_way_table="Account",
        action_main="X01",
        action_main_type="Income",
        action_main_table="Code_Data",
        spending=5000.0,
    )
    base.update(overrides)
    return Journal(**base)


def test_cash_flow_happy(client: TestClient, session: Session) -> None:
    session.add(_journal(action_main_type="Income", spending=5000.0))
    session.add(_journal(action_main_type="Fixed", spending=-1000.0))
    session.add(LoanJournal(loan_id="LN-1", loan_excute_type="principal", excute_price=2000.0, excute_date="20260315"))
    session.commit()

    r = client.get("/reports/cash-flow/monthly?vesting_month=202612")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["type"] == "monthly"
    summary = data["summary"]
    assert [a["key"] for a in summary["activities"]] == ["operating", "investing", "financing"]
    by = {a["key"]: a for a in summary["activities"]}
    assert by["operating"]["net"] == 4000.0  # 5000 - 1000
    assert by["financing"]["net"] == -2000.0
    assert summary["net_change"] == 2000.0

    # Per-period series: 202603 carries the flow; net_change ties to the summary.
    assert len(data["points"]) == 12
    pt = {p["period"]: p for p in data["points"]}
    assert pt["202603"]["operating"] == 4000.0
    assert pt["202603"]["financing"] == -2000.0
    assert pt["202603"]["net_change"] == 2000.0
    assert sum(p["net_change"] for p in data["points"]) == summary["net_change"]


def test_cash_flow_buckets_by_period(client: TestClient, session: Session) -> None:
    session.add(_journal(vesting_month="202602", spend_date="20260201", action_main_type="Income", spending=3000.0))
    session.add(_journal(vesting_month="202604", spend_date="20260401", action_main_type="Invest", spending=-800.0))
    session.commit()

    data = client.get("/reports/cash-flow/monthly?vesting_month=202612").json()["data"]
    pt = {p["period"]: p for p in data["points"]}
    assert pt["202602"]["operating"] == 3000.0
    assert pt["202602"]["net_change"] == 3000.0
    assert pt["202604"]["investing"] == -800.0
    assert pt["202604"]["net_change"] == -800.0
    assert pt["202603"]["net_change"] == 0.0  # untouched month
    assert data["summary"]["net_change"] == 2200.0  # 3000 - 800


def test_cash_flow_invalid_type_returns_422(client: TestClient) -> None:
    r = client.get("/reports/cash-flow/weekly?vesting_month=202412")
    assert r.status_code == 422


def test_cash_flow_invalid_month_returns_422(client: TestClient) -> None:
    r = client.get("/reports/cash-flow/monthly?vesting_month=2024")
    assert r.status_code == 422
