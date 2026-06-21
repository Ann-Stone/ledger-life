"""Field-level tests for Loan and LoanJournal tables."""
from __future__ import annotations

from app.models.assets.loan import (
    Loan,
    LoanCreate,
    LoanJournal,
    LoanJournalCreate,
    LoanJournalRead,
    LoanJournalUpdate,
    LoanRead,
    LoanUpdate,
)


def _check(*classes) -> None:
    for cls in classes:
        js = cls.model_json_schema()
        assert "example" in js, cls.__name__
        for n, p in js["properties"].items():
            assert "description" in p, f"{cls.__name__}.{n}"
            assert "examples" in p, f"{cls.__name__}.{n}"


def test_loan_fields() -> None:
    table = Loan.__table__
    assert Loan.__tablename__ == "Loan"
    assert table.c.loan_id.primary_key is True

    expected = {
        "loan_id",
        "loan_name",
        "loan_type",
        "account_id",
        "account_name",
        "interest_rate",
        "period",
        "apply_date",
        "grace_expire_date",
        "pay_day",
        "amount",
        "repayed",
        "loan_index",
    }
    assert set(table.c.keys()) == expected
    _check(Loan, LoanCreate, LoanUpdate, LoanRead)


def test_loan_journal_fields() -> None:
    table = LoanJournal.__table__
    assert LoanJournal.__tablename__ == "Loan_Journal"
    assert table.c.distinct_number.primary_key is True

    expected = {"distinct_number", "loan_id", "loan_excute_type", "excute_price", "excute_date", "memo"}
    assert set(table.c.keys()) == expected
    _check(LoanJournal, LoanJournalCreate, LoanJournalUpdate, LoanJournalRead)
