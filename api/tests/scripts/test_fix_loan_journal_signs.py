"""Tests for the one-off Loan_Journal sign-normalization fix script."""
from __future__ import annotations

from sqlmodel import Session, select

from app.models.assets.loan import Loan, LoanJournal
from app.scripts.fix_loan_journal_signs import fix_loan_journal_signs


def _loan(session: Session, loan_id: str, amount: float = 1_000_000.0) -> None:
    session.add(
        Loan(
            loan_id=loan_id,
            loan_name="Mortgage",
            loan_type="mortgage",
            account_id="BANK-01",
            account_name="Bank",
            interest_rate=0.0131,
            period=360,
            apply_date="20200101",
            grace_expire_date=None,
            pay_day=1,
            amount=amount,
            repayed=0.0,
            loan_index=1,
        )
    )


def _journal(session: Session, loan_id: str, excute_type: str, price: float) -> None:
    session.add(
        LoanJournal(
            loan_id=loan_id,
            loan_excute_type=excute_type,
            excute_price=price,
            excute_date="20250115",
            memo="seed",
        )
    )


def _mixed_sign_fixture(session: Session) -> None:
    """LN-001 has negative + positive rows; LN-002 is already all-positive."""
    _loan(session, "LN-001")
    _journal(session, "LN-001", "principal", -23206.0)  # legacy negative
    _journal(session, "LN-001", "principal", -100.0)    # legacy negative
    _journal(session, "LN-001", "principal", 5000.0)    # newer endpoint positive
    _journal(session, "LN-001", "interest", -50.0)      # stray negative interest
    _journal(session, "LN-001", "fee", 30.0)            # already positive
    _loan(session, "LN-002")
    _journal(session, "LN-002", "principal", 800.0)     # never negative
    session.commit()


def _prices(session: Session, loan_id: str) -> list[float]:
    return sorted(
        j.excute_price
        for j in session.exec(
            select(LoanJournal).where(LoanJournal.loan_id == loan_id)
        ).all()
    )


def test_flips_negatives_and_recalculates_repayed(session: Session) -> None:
    _mixed_sign_fixture(session)

    report = fix_loan_journal_signs(session)

    # Only LN-001 had negatives (3 of them: two principal, one interest).
    assert report.negatives_by_loan == {"LN-001": 3}
    assert report.total_negatives == 3
    assert report.rows_flipped == 3
    assert report.loans_recalculated == ["LN-001"]

    # No negative magnitudes survive anywhere.
    assert all(
        j.excute_price >= 0 for j in session.exec(select(LoanJournal)).all()
    )
    assert _prices(session, "LN-001") == [30.0, 50.0, 100.0, 5000.0, 23206.0]

    # repayed = sum of principal magnitudes (23206 + 100 + 5000), not interest/fee.
    assert session.get(Loan, "LN-001").repayed == 28306.0
    # LN-002 was never negative and stays untouched.
    assert session.get(Loan, "LN-002").repayed == 0.0
    assert _prices(session, "LN-002") == [800.0]


def test_idempotent_second_run_is_a_noop(session: Session) -> None:
    _mixed_sign_fixture(session)

    fix_loan_journal_signs(session)
    after_first = _prices(session, "LN-001")
    repayed_first = session.get(Loan, "LN-001").repayed

    report2 = fix_loan_journal_signs(session)

    assert report2.total_negatives == 0
    assert report2.rows_flipped == 0
    assert report2.loans_recalculated == []
    assert _prices(session, "LN-001") == after_first
    assert session.get(Loan, "LN-001").repayed == repayed_first


def test_dry_run_reports_without_writing(session: Session) -> None:
    _mixed_sign_fixture(session)

    report = fix_loan_journal_signs(session, dry_run=True)

    assert report.dry_run is True
    assert report.negatives_by_loan == {"LN-001": 3}
    assert report.total_negatives == 3
    assert report.rows_flipped == 0
    assert report.loans_recalculated == []
    # Nothing was written: the negatives are still negative.
    assert any(
        j.excute_price < 0 for j in session.exec(select(LoanJournal)).all()
    )
    assert session.get(Loan, "LN-001").repayed == 0.0


def test_clean_db_reports_nothing(session: Session) -> None:
    _loan(session, "LN-001")
    _journal(session, "LN-001", "principal", 1500.0)
    session.commit()

    report = fix_loan_journal_signs(session)

    assert report.negatives_by_loan == {}
    assert report.total_negatives == 0
    assert report.rows_flipped == 0
