"""Budget variance (預算 vs 實際) endpoint tests."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.monthly_report.journal import Journal
from app.models.settings.budget import Budget


def _budget(**overrides) -> Budget:
    base = dict(
        budget_year="2026",
        category_code="F01",
        category_name="居住",
        code_type="Fixed",
        annual_amount=None,
    )
    for m in range(1, 13):
        base[f"expected{m:02d}"] = 30000.0
    base.update(overrides)
    return Budget(**base)


def _journal(**overrides) -> Journal:
    base = dict(
        vesting_month="202601",
        spend_date="20260105",
        spend_way="A1",
        spend_way_type="account",
        spend_way_table="Account",
        action_main="F01",
        action_main_type="Fixed",
        action_main_table="Code_Data",
        spending=-30000.0,
    )
    base.update(overrides)
    return Journal(**base)


def test_budget_variance_happy(client: TestClient, session: Session) -> None:
    session.add(_budget())
    session.add(_journal())
    session.commit()

    r = client.get("/reports/budget-variance/2026")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["year"] == "2026"
    assert data["rows"][0]["code"] == "F01"
    assert data["rows"][0]["expected"] == 360000.0
    assert data["rows"][0]["actual"] == 30000.0
    assert data["summary"]["total_expected"] == 360000.0


def test_budget_variance_invalid_year_returns_422(client: TestClient) -> None:
    r = client.get("/reports/budget-variance/20")
    assert r.status_code == 422
