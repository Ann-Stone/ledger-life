"""Income statement (收支表) endpoint tests."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.monthly_report.journal import Journal


def _journal(**overrides) -> Journal:
    base = dict(
        vesting_month="202604",
        spend_date="20260410",
        spend_way="A1",
        spend_way_type="account",
        spend_way_table="Account",
        action_main="X01",
        action_main_type="Floating",
        action_main_table="Code_Data",
        spending=-100.0,
    )
    base.update(overrides)
    return Journal(**base)


def test_income_expense_monthly_happy(client: TestClient, session: Session) -> None:
    session.add(_journal(action_main="I01", action_main_type="Income", spending=5000.0))
    session.add(_journal(action_main="F01", action_main_type="Fixed", spending=-200.0))
    session.commit()

    r = client.get("/reports/income-expense/monthly?vesting_month=202604")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["type"] == "monthly"
    assert len(data["points"]) == 12
    assert data["points"][-1]["period"] == "202604"
    assert data["summary"]["total_income"] == 5000.0
    assert data["summary"]["total_expense"] == 200.0
    assert data["summary"]["net"] == 4800.0
    assert data["summary"]["savings_rate"] == 0.96


def test_income_expense_loan_repayment_is_additive_only(
    client: TestClient, session: Session
) -> None:
    """Loan repayment surfaces as the additive ``point.loan_repayment`` field but
    must NOT change expense / net / savings_rate (those stay consumption-basis)."""
    from app.models.assets.loan import LoanJournal

    session.add(_journal(action_main="I01", action_main_type="Income", spending=5000.0))
    session.add(_journal(action_main="F01", action_main_type="Fixed", spending=-200.0))
    # Report-neutral loan Journal + its Loan_Journal legs (principal 8000 + interest 1200).
    session.add(_journal(action_main="LoanRepayment", action_main_type="LoanRepayment",
                         action_main_table="Loan", spending=-9200.0))
    session.add(LoanJournal(loan_id="LN-001", loan_excute_type="principal",
                            excute_price=8000.0, excute_date="20260410"))
    session.add(LoanJournal(loan_id="LN-001", loan_excute_type="interest",
                            excute_price=1200.0, excute_date="20260410"))
    session.commit()

    data = client.get("/reports/income-expense/monthly?vesting_month=202604").json()["data"]
    last = data["points"][-1]
    assert last["period"] == "202604"
    # New additive field reflects the full cash outflow (principal + interest).
    assert last["loan_repayment"] == 9200.0
    # Aggregates are UNCHANGED vs the happy-path test (loan excluded from them).
    assert last["expense"] == 200.0
    assert data["summary"]["total_expense"] == 200.0
    assert data["summary"]["net"] == 4800.0
    assert data["summary"]["savings_rate"] == 0.96


def test_income_expense_invalid_type_returns_422(client: TestClient) -> None:
    r = client.get("/reports/income-expense/weekly?vesting_month=202412")
    assert r.status_code == 422


def test_income_expense_invalid_month_returns_422(client: TestClient) -> None:
    r = client.get("/reports/income-expense/monthly?vesting_month=2024")
    assert r.status_code == 422
