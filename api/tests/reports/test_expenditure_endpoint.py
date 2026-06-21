"""BE-025 — expenditure trend endpoint tests."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.monthly_report.journal import Journal


def test_get_expenditure_monthly_happy(client: TestClient, session: Session) -> None:
    session.add(
        Journal(
            vesting_month="202604",
            spend_date="20260410",
            spend_way="A1",
            spend_way_type="account",
            spend_way_table="Account",
            action_main="E01",
            action_main_type="Floating",
            action_main_table="Code_Data",
            spending=-100.0,
        )
    )
    session.commit()

    r = client.get("/reports/expenditure/monthly?vesting_month=202604")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["type"] == "monthly"
    assert len(data["points"]) == 12
    last = data["points"][-1]
    assert last["period"] == "202604"
    assert last["amount"] == 100.0


def test_get_expenditure_invalid_type_returns_422(client: TestClient) -> None:
    r = client.get("/reports/expenditure/weekly?vesting_month=202412")
    assert r.status_code == 422


def test_get_expenditure_invalid_month_returns_422(client: TestClient) -> None:
    r = client.get("/reports/expenditure/monthly?vesting_month=2024")
    assert r.status_code == 422
