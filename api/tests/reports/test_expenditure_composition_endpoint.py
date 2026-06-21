"""Expenditure composition (支出結構) endpoint tests."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.monthly_report.journal import Journal
from app.models.settings.code_data import CodeData


def _journal(**overrides) -> Journal:
    base = dict(
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
    base.update(overrides)
    return Journal(**base)


def test_composition_monthly_happy(client: TestClient, session: Session) -> None:
    session.add(CodeData(code_id="E01", code_type="Floating", name="餐飲", in_use="Y", code_index=1))
    session.add(CodeData(code_id="F01", code_type="Fixed", name="房租", in_use="Y", code_index=2))
    session.add(_journal(action_main="E01", action_main_type="Floating", spending=-300.0))
    session.add(_journal(action_main="F01", action_main_type="Fixed", spending=-700.0))
    session.commit()

    r = client.get("/reports/expenditure-composition/monthly?vesting_month=202604")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 1000.0
    assert data["fixed_total"] == 700.0
    assert data["floating_total"] == 300.0
    assert [c["code"] for c in data["categories"]] == ["F01", "E01"]
    assert data["categories"][0]["name"] == "房租"


def test_composition_invalid_type_returns_422(client: TestClient) -> None:
    r = client.get("/reports/expenditure-composition/weekly?vesting_month=202412")
    assert r.status_code == 422


def test_composition_invalid_month_returns_422(client: TestClient) -> None:
    r = client.get("/reports/expenditure-composition/monthly?vesting_month=2024")
    assert r.status_code == 422
