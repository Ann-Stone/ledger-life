"""Retirement-readiness (Part B/C) tests: settings, readiness, payoff projection."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.assets.loan import Loan, LoanJournal
from app.models.dashboard.retirement import RetirementSettingUpdate
from app.models.monthly_report.account_balance import AccountBalance
from app.models.monthly_report.estate_net_value_history import EstateNetValueHistory
from app.models.monthly_report.journal import Journal
from app.services.retirement_service import (
    get_retirement_readiness,
    get_retirement_settings,
    update_retirement_settings,
)


def _journal(session: Session, **ov) -> None:
    base = dict(
        vesting_month="202606", spend_date="20260615", spend_way="A1",
        spend_way_type="account", spend_way_table="Account",
        action_main="X01", action_main_type="Floating", action_main_table="Code_Data",
        action_sub=None, action_sub_type=None, action_sub_table=None,
        spending=-100.0, invoice_number=None, note=None,
    )
    base.update(ov)
    session.add(Journal(**base))


def _net_worth(session: Session, amount: float) -> None:
    session.add(AccountBalance(vesting_month="202612", id="ACC-1", name="Bank",
                               balance=amount, fx_code="TWD", fx_rate=1.0, is_calculate="Y"))


def _estate(session: Session, *, est_id: str, value: float, status: str) -> None:
    session.add(EstateNetValueHistory(
        vesting_month="202612", id=est_id, asset_id="AC-REAL-001", name=est_id,
        market_value=value, cost=value, estate_status=status, fx_code="TWD", fx_rate=1.0,
    ))


# ---------- Settings ----------


def test_retirement_settings_defaults_and_roundtrip(client: TestClient) -> None:
    got = client.get("/dashboard/retirement-settings").json()["data"]
    assert got == {
        "withdrawal_rate": 0.04,
        "annual_expense_override": None,
        "exclude_self_occupied_estate": True,
    }

    put = client.put(
        "/dashboard/retirement-settings",
        json={"withdrawal_rate": 0.035, "annual_expense_override": 600000.0},
    )
    assert put.status_code == 200
    assert put.json()["data"] == {
        "withdrawal_rate": 0.035,
        "annual_expense_override": 600000.0,
        "exclude_self_occupied_estate": True,
    }

    again = client.get("/dashboard/retirement-settings").json()["data"]
    assert again == {
        "withdrawal_rate": 0.035,
        "annual_expense_override": 600000.0,
        "exclude_self_occupied_estate": True,
    }

    # null clears the override; rate omitted keeps current; toggle persists.
    cleared = client.put(
        "/dashboard/retirement-settings",
        json={"annual_expense_override": None, "exclude_self_occupied_estate": False},
    ).json()["data"]
    assert cleared == {
        "withdrawal_rate": 0.035,
        "annual_expense_override": None,
        "exclude_self_occupied_estate": False,
    }


def test_retirement_settings_rejects_bad_rate(client: TestClient) -> None:
    r = client.put("/dashboard/retirement-settings", json={"withdrawal_rate": 0.9})
    assert r.status_code == 422


# ---------- Readiness (consumption basis) ----------


def test_readiness_expense_base_excludes_loan(session: Session) -> None:
    _net_worth(session, 8_000_000.0)
    # Trailing-12m income 1,080,000 (→ 90,000/mo); consumption 360,000 (fixed+floating).
    _journal(session, action_main="INC01", action_main_type="Income", spending=1_080_000.0)
    _journal(session, action_main="FIX01", action_main_type="Fixed", spending=-240_000.0)
    _journal(session, action_main="FLT01", action_main_type="Floating", spending=-120_000.0)
    # Report-neutral loan Journal (must NOT enter the expense base) + Loan_Journal legs.
    _journal(session, action_main="LoanRepayment", action_main_type="LoanRepayment",
             action_main_table="Loan", spending=-336_000.0)
    session.add(LoanJournal(loan_id="LN-001", loan_excute_type="principal",
                            excute_price=300_000.0, excute_date="20260615"))
    session.add(LoanJournal(loan_id="LN-001", loan_excute_type="interest",
                            excute_price=36_000.0, excute_date="20260615"))
    session.commit()

    r = get_retirement_readiness(session, as_of="202612")

    # Expense base = fixed + floating only (loan excluded), source computed.
    assert r.annual_expense_base == 360_000.0
    assert r.expense_base_source == "computed"
    assert r.withdrawal_rate == 0.04
    assert r.target_portfolio == 9_000_000.0          # 360k / 0.04
    assert r.readiness_pct == 0.8889                  # 8M / 9M
    assert r.gap == 1_000_000.0
    # Debt-service health: loan payment is visible here (from Loan_Journal).
    assert r.monthly_income == 90_000.0
    assert r.monthly_loan_payment == 28_000.0         # 336k / 12
    assert r.debt_service_ratio == 0.3111             # 336k / 1080k


def test_readiness_override_base(session: Session) -> None:
    _net_worth(session, 5_000_000.0)
    _journal(session, action_main="FIX01", action_main_type="Fixed", spending=-99_999.0)
    update_retirement_settings(session, RetirementSettingUpdate(annual_expense_override=500_000.0))

    r = get_retirement_readiness(session, as_of="202612")
    assert r.expense_base_source == "override"
    assert r.annual_expense_base == 500_000.0
    assert r.target_portfolio == 12_500_000.0         # 500k / 0.04
    assert r.readiness_pct == 0.4                      # 5M / 12.5M


# ---------- Self-occupied housing exclusion ----------


def test_readiness_excludes_self_occupied_estate_by_default(session: Session) -> None:
    # Net worth 10M = 5M cash + 3M self-occupied (live) + 2M rented (rent).
    _net_worth(session, 5_000_000.0)
    _estate(session, est_id="HOME", value=3_000_000.0, status="live")
    _estate(session, est_id="RENTAL", value=2_000_000.0, status="rent")
    _journal(session, action_main="FIX01", action_main_type="Fixed", spending=-400_000.0)
    session.commit()

    r = get_retirement_readiness(session, as_of="202612")

    # Default toggle on → the 3M self-occupied home drops out; rental stays in.
    assert r.exclude_self_occupied_estate is True
    assert r.self_occupied_estate_value == 3_000_000.0
    assert r.net_worth == 7_000_000.0                 # 10M − 3M home
    assert r.target_portfolio == 10_000_000.0         # 400k / 0.04
    assert r.readiness_pct == 0.7                      # 7M / 10M
    assert r.gap == 3_000_000.0


def test_readiness_includes_estate_when_toggle_off(session: Session) -> None:
    _net_worth(session, 5_000_000.0)
    _estate(session, est_id="HOME", value=3_000_000.0, status="live")
    _estate(session, est_id="RENTAL", value=2_000_000.0, status="rent")
    _journal(session, action_main="FIX01", action_main_type="Fixed", spending=-400_000.0)
    update_retirement_settings(
        session, RetirementSettingUpdate(exclude_self_occupied_estate=False)
    )

    r = get_retirement_readiness(session, as_of="202612")

    assert r.exclude_self_occupied_estate is False
    assert r.self_occupied_estate_value == 0.0
    assert r.net_worth == 10_000_000.0                # full balance sheet
    assert r.readiness_pct == 1.0                      # 10M / 10M


def test_readiness_no_self_occupied_estate_excludes_nothing(session: Session) -> None:
    # "可以都不選自住": no estate marked 'live' → nothing excluded even with toggle on.
    _net_worth(session, 5_000_000.0)
    _estate(session, est_id="RENTAL", value=2_000_000.0, status="rent")
    _journal(session, action_main="FIX01", action_main_type="Fixed", spending=-400_000.0)
    session.commit()

    r = get_retirement_readiness(session, as_of="202612")

    assert r.exclude_self_occupied_estate is True
    assert r.self_occupied_estate_value == 0.0
    assert r.net_worth == 7_000_000.0                 # 5M cash + 2M rental, unchanged


# ---------- Payoff projection ----------


def test_loan_payoff_projection(session: Session) -> None:
    session.add(Loan(
        loan_id="LN-001", loan_name="房貸", loan_type="mortgage",
        account_id="ACC-1", account_name="Bank", interest_rate=0.02, period=360,
        apply_date="20200101", pay_day=1, amount=1_000_000.0, repayed=400_000.0, loan_index=1,
    ))
    # 12 monthly legs across the trailing window of anchor 202612 (202601..202612):
    # principal 10,000 + interest 2,000 each → avg principal 10,000/mo.
    for m in range(1, 13):
        date = f"2026{m:02d}10"
        session.add(LoanJournal(loan_id="LN-001", loan_excute_type="principal",
                                excute_price=10_000.0, excute_date=date))
        session.add(LoanJournal(loan_id="LN-001", loan_excute_type="interest",
                                excute_price=2_000.0, excute_date=date))
    session.commit()

    r = get_retirement_readiness(session, as_of="202612")
    assert len(r.loans) == 1
    loan = r.loans[0]
    assert loan.remaining_balance == 600_000.0        # 1,000,000 − 400,000
    assert loan.monthly_payment == 12_000.0           # (120k + 24k) / 12
    assert loan.years_left == 5.0                      # 600k / 10k = 60 months
    assert loan.payoff_month == "203112"              # 202612 + 60 months


def test_retirement_endpoint_smoke(client: TestClient) -> None:
    r = client.get("/dashboard/retirement")
    assert r.status_code == 200
    data = r.json()["data"]
    for key in (
        "net_worth", "exclude_self_occupied_estate", "self_occupied_estate_value",
        "annual_expense_base", "expense_base_source", "withdrawal_rate",
        "target_portfolio", "readiness_pct", "gap", "monthly_income",
        "monthly_loan_payment", "debt_service_ratio", "loans",
    ):
        assert key in data
