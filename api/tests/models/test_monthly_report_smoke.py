"""Round-trip smoke test for the Monthly Report domain tables."""
from __future__ import annotations

from sqlmodel import Session, select

from app.models.monthly_report import (
    AccountBalance,
    CreditCardBalance,
    EstateNetValueHistory,
    InsuranceNetValueHistory,
    Journal,
    LoanBalance,
    StockNetValueHistory,
)


def test_monthly_report_models_roundtrip(session: Session) -> None:
    journal = Journal(
        vesting_month="202604",
        spend_date="20260418",
        spend_way="BANK-CHASE-01",
        spend_way_type="account",
        spend_way_table="Account",
        action_main="EXP01",
        action_main_type="expense",
        action_main_table="Code_Data",
        spending=-123.45,
        note="Lunch",
    )
    account_bal = AccountBalance(
        vesting_month="202604",
        id="BANK-CHASE-01",
        name="Chase Checking",
        balance=12345.67,
        fx_code="USD",
        fx_rate=31.5,
        is_calculate="Y",
    )
    credit_bal = CreditCardBalance(
        vesting_month="202604",
        id="CC-VISA-01",
        name="Chase Sapphire",
        balance=-2500.0,
        fx_rate=31.5,
    )
    estate_hist = EstateNetValueHistory(
        vesting_month="202604",
        id="EST-001",
        asset_id="AC-REAL-001",
        name="Condo",
        market_value=500000.0,
        cost=420000.0,
        estate_status="hold",
        fx_code="TWD",
        fx_rate=1.0,
    )
    ins_hist = InsuranceNetValueHistory(
        vesting_month="202604",
        id="INS-001",
        asset_id="AC-INS-001",
        name="Whole life",
        surrender_value=25000.0,
        cost=20000.0,
        fx_code="USD",
        fx_rate=31.5,
    )
    loan_bal = LoanBalance(
        vesting_month="202604",
        id="LN-001",
        name="Mortgage",
        balance=-250000.0,
        cost=250000.0,
        fx_code="TWD",
        fx_rate=1.0,
    )
    stock_hist = StockNetValueHistory(
        vesting_month="202604",
        id="STK-H-001",
        asset_id="AC-STK-001",
        stock_code="AAPL",
        stock_name="Apple Inc.",
        amount=100.0,
        price=180.5,
        cost=15000.0,
        fx_code="USD",
        fx_rate=31.5,
    )

    session.add_all([journal, account_bal, credit_bal, estate_hist, ins_hist, loan_bal, stock_hist])
    session.commit()

    got_journal = session.exec(select(Journal)).one()
    assert got_journal.distinct_number is not None
    assert got_journal.spending == -123.45

    assert session.exec(
        select(AccountBalance).where(AccountBalance.id == "BANK-CHASE-01")
    ).one().balance == 12345.67
    assert session.exec(
        select(CreditCardBalance).where(CreditCardBalance.id == "CC-VISA-01")
    ).one().balance == -2500.0
    assert session.exec(
        select(EstateNetValueHistory).where(EstateNetValueHistory.id == "EST-001")
    ).one().market_value == 500000.0
    assert session.exec(
        select(InsuranceNetValueHistory).where(InsuranceNetValueHistory.id == "INS-001")
    ).one().surrender_value == 25000.0
    assert session.exec(
        select(LoanBalance).where(LoanBalance.id == "LN-001")
    ).one().balance == -250000.0
    assert session.exec(
        select(StockNetValueHistory).where(StockNetValueHistory.id == "STK-H-001")
    ).one().price == 180.5
