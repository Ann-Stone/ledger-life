"""Expense insights (年度洞察) endpoint tests."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.monthly_report.journal import Journal
from app.models.settings.code_data import CodeData


def _journal(**overrides) -> Journal:
    base = dict(
        vesting_month="202603",
        spend_date="20260305",
        spend_way="A1",
        spend_way_type="account",
        spend_way_table="Account",
        action_main="E01",
        action_main_type="Floating",
        action_main_table="Code_Data",
        spending=-150.0,
    )
    base.update(overrides)
    return Journal(**base)


def test_expense_insights_happy(client: TestClient, session: Session) -> None:
    session.add(CodeData(code_id="E01", code_type="Floating", name="餐飲", in_use="Y", code_index=1))
    session.add(_journal(action_main="E01", action_main_type="Floating", spending=-150.0))
    session.commit()

    r = client.get("/reports/expense-insights/2026")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["year"] == "2026"
    assert data["largest"][0]["amount"] == 150.0
    assert data["largest"][0]["category"] == "餐飲"


def test_expense_insights_invalid_year_returns_422(client: TestClient) -> None:
    r = client.get("/reports/expense-insights/20")
    assert r.status_code == 422
