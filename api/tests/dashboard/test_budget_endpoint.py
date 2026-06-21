"""BE-026 — budget endpoint tests."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.monthly_report.journal import Journal
from app.models.settings.budget import Budget
from app.models.settings.code_data import CodeData


def _event_code(session: Session, code_id: str, name: str) -> None:
    session.add(
        CodeData(
            code_id=code_id,
            code_type="Floating",
            name=name,
            in_use="Y",
            code_index=1,
            is_annual_event=True,
        )
    )


def _journal(session: Session, vm: str, action_main: str, spending: float, action_main_type: str = "Floating") -> None:
    session.add(
        Journal(
            vesting_month=vm,
            spend_date=f"{vm}15",
            spend_way="A",
            spend_way_type="account",
            spend_way_table="Account",
            action_main=action_main,
            action_main_type=action_main_type,
            action_main_table="Code_Data",
            spending=spending,
        )
    )


def test_get_budget_monthly_happy(client: TestClient, session: Session) -> None:
    session.add(
        Budget(
            budget_year="2026",
            category_code="F01",
            category_name="Rent",
            code_type="Fixed",
            **{f"expected{m:02d}": 10000.0 if m == 4 else 0.0 for m in range(1, 13)},
        )
    )
    session.commit()

    r = client.get("/dashboard/budget?type=monthly&period=202604")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["type"] == "monthly"
    assert data["period"] == "202604"
    line = next(l for l in data["lines"] if l["category"] == "Rent")
    assert line["planned"] == 10000.0


def test_get_budget_monthly_golden(client: TestClient, session: Session) -> None:
    session.add(
        Budget(
            budget_year="2026",
            category_code="F01",
            category_name="Rent",
            code_type="Fixed",
            **{f"expected{m:02d}": 10000.0 for m in range(1, 13)},
        )
    )
    session.add(
        Journal(
            vesting_month="202604",
            spend_date="20260410",
            spend_way="A1",
            spend_way_type="account",
            spend_way_table="Account",
            action_main="F01",
            action_main_type="Fixed",
            action_main_table="Code_Data",
            spending=-7500.0,
        )
    )
    session.commit()

    r = client.get("/dashboard/budget?type=monthly&period=202604")
    data = r.json()["data"]
    line = next(l for l in data["lines"] if l["category"] == "Rent")
    assert line["planned"] == 10000.0
    assert line["actual"] == 7500.0
    assert line["usage_pct"] == 75.0


def test_get_budget_invalid_period_returns_422(client: TestClient) -> None:
    r = client.get("/dashboard/budget?type=monthly&period=24-03")
    assert r.status_code == 422


def test_monthly_splits_event_into_event_lines(client: TestClient, session: Session) -> None:
    _event_code(session, "EV1", "LunarNY")
    session.add(
        Budget(
            budget_year="2026",
            category_code="EV1",
            category_name="LunarNY",
            code_type="Floating",
            annual_amount=12000.0,
            **{f"expected{m:02d}": 0.0 for m in range(1, 13)},
        )
    )
    session.add(
        Budget(
            budget_year="2026",
            category_code="F01",
            category_name="Rent",
            code_type="Fixed",
            **{f"expected{m:02d}": 10000.0 for m in range(1, 13)},
        )
    )
    _journal(session, "202601", "EV1", -3000.0)  # YTD part 1
    _journal(session, "202602", "EV1", -4000.0)  # YTD part 2
    _journal(session, "202602", "F01", -9000.0, action_main_type="Fixed")
    session.commit()

    data = client.get("/dashboard/budget?type=monthly&period=202602").json()["data"]
    assert "LunarNY" not in {l["category"] for l in data["lines"]}
    assert "Rent" in {l["category"] for l in data["lines"]}
    # ordinary totals exclude the event spend
    assert data["total_actual"] == 9000.0
    ev = next(l for l in data["event_lines"] if l["category"] == "LunarNY")
    assert ev["planned"] == 12000.0
    assert ev["actual"] == 7000.0  # year-to-date Jan + Feb
    assert data["event_total_planned"] == 12000.0


def test_yearly_includes_event_envelope(client: TestClient, session: Session) -> None:
    _event_code(session, "EV1", "LunarNY")
    session.add(
        Budget(
            budget_year="2026",
            category_code="EV1",
            category_name="LunarNY",
            code_type="Floating",
            annual_amount=12000.0,
            **{f"expected{m:02d}": 0.0 for m in range(1, 13)},
        )
    )
    _journal(session, "202603", "EV1", -5000.0)
    session.commit()

    data = client.get("/dashboard/budget?type=yearly&period=2026").json()["data"]
    ev = next(l for l in data["event_lines"] if l["category"] == "LunarNY")
    assert ev["planned"] == 12000.0
    assert ev["actual"] == 5000.0
