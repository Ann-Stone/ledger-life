"""Round-trip smoke test for the Asset domain tables."""
from __future__ import annotations

from sqlmodel import Session, select

from app.models.assets import (
    Estate,
    EstateJournal,
    Insurance,
    InsuranceJournal,
    Loan,
    LoanJournal,
    OtherAsset,
    StockDetail,
    StockJournal,
)


def test_assets_models_roundtrip(session: Session) -> None:
    other = OtherAsset(
        asset_id="AC-STK-001",
        asset_name="US equities",
        asset_type="stock",
        in_use="Y",
        asset_index=1,
    )
    sj = StockJournal(
        stock_id="STK-H-001",
        stock_code="AAPL",
        stock_name="Apple Inc.",
        asset_id="AC-STK-001",
        expected_spend=10000.0,
    )
    sd = StockDetail(
        stock_id="STK-H-001",
        excute_type="buy",
        excute_amount=10.0,
        excute_price=180.5,
        excute_date="20260418",
        account_id="BANK-CHASE-01",
        account_name="Chase Checking",
        memo="Initial buy",
    )
    ins = Insurance(
        insurance_id="INS-001",
        insurance_name="Whole life policy",
        asset_id="AC-INS-001",
        in_account="BANK-CHASE-01",
        out_account="BANK-CHASE-01",
        start_date="20200101",
        end_date="20500101",
        pay_type="annual",
        pay_day="01/15",
        expected_spend=1200.0,
        has_closed="N",
    )
    inj = InsuranceJournal(
        insurance_id="INS-001",
        insurance_excute_type="pay",
        excute_price=1200.0,
        excute_date="20260115",
        memo="Annual premium",
    )
    est = Estate(
        estate_id="EST-001",
        estate_name="Condo",
        estate_type="residential",
        estate_address="123 Main St",
        asset_id="AC-REAL-001",
        obtain_date="20200101",
        loan_id="LN-001",
        estate_status="hold",
        memo="Primary residence",
    )
    estj = EstateJournal(
        estate_id="EST-001",
        estate_excute_type="purchase",
        excute_price=500000.0,
        excute_date="20200101",
        memo="Closing",
    )
    loan = Loan(
        loan_id="LN-001",
        loan_name="Mortgage",
        loan_type="mortgage",
        account_id="BANK-CHASE-01",
        account_name="Chase Checking",
        interest_rate=0.035,
        period=360,
        apply_date="20200101",
        grace_expire_date="20200401",
        pay_day=1,
        amount=250000.0,
        repayed=12500.0,
        loan_index=1,
    )
    lj = LoanJournal(
        loan_id="LN-001",
        loan_excute_type="repayment",
        excute_price=1500.0,
        excute_date="20260401",
        memo="April payment",
    )

    session.add_all([other, sj, sd, ins, inj, est, estj, loan, lj])
    session.commit()

    assert session.exec(select(OtherAsset)).one().asset_id == "AC-STK-001"
    assert session.exec(select(StockJournal)).one().stock_code == "AAPL"
    assert session.exec(select(StockDetail)).one().excute_amount == 10.0
    assert session.exec(select(Insurance)).one().insurance_name == "Whole life policy"
    assert session.exec(select(InsuranceJournal)).one().excute_price == 1200.0
    assert session.exec(select(Estate)).one().estate_status == "hold"
    assert session.exec(select(EstateJournal)).one().excute_price == 500000.0
    assert session.exec(select(Loan)).one().interest_rate == 0.035
    assert session.exec(select(LoanJournal)).one().excute_price == 1500.0
