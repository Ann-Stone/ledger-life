"""Composite endpoint: POST /monthly-report/journals/loan-transaction.

A loan repayment splits into a principal portion and an interest portion, each
written as its own Loan_Journal row holding a POSITIVE magnitude (not a signed
copy of journal.spending). The journal's signed spending is the total outflow,
−(principal+interest); the service validates the two agree and recomputes
Loan.repayed. Covers the split, validation guards, rollback, the update path and
a router smoke pass.
"""
from __future__ import annotations

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.assets.loan import Loan, LoanJournal
from app.models.monthly_report.journal import Journal, JournalCreate, JournalUpdate
from app.models.monthly_report.journal_composite import (
    JournalLoanTransactionCreate,
    JournalLoanTransactionUpdate,
    LoanTransactionDetailCreate,
)
from app.services.monthly_report_service import (
    create_journal,
    create_journal_with_loan_transaction,
    update_journal_with_loan_transaction,
)


# ---------------------------------------------------------------- helpers ----


def _loan(session: Session, loan_id: str = "LN-001", amount: float = 250000.0) -> Loan:
    loan = Loan(
        loan_id=loan_id,
        loan_name="Mortgage",
        loan_type="mortgage",
        account_id="BANK-CHASE-01",
        account_name="Chase Checking",
        interest_rate=0.035,
        period=360,
        apply_date="20200101",
        grace_expire_date=None,
        pay_day=1,
        amount=amount,
        repayed=0.0,
        loan_index=1,
    )
    session.add(loan)
    session.commit()
    session.refresh(loan)
    return loan


def _journal(**overrides) -> dict:
    base = {
        "vesting_month": "202604",
        "spend_date": "20260401",
        "spend_way": "1",
        "spend_way_type": "account",
        "spend_way_table": "Account",
        "action_main": "LoanRepayment",
        "action_main_type": "LoanRepayment",
        "action_main_table": "Loan",
        "action_sub": "LN-001",
        "action_sub_type": "Loan",
        "action_sub_table": "Loan",
        "spending": -9200.0,
        "invoice_number": None,
        "note": "April payment",
    }
    base.update(overrides)
    return base


def _payload(
    *, journal_overrides: dict | None = None, **detail_kwargs
) -> JournalLoanTransactionCreate:
    return JournalLoanTransactionCreate(
        journal=JournalCreate(**_journal(**(journal_overrides or {}))),
        loan_detail=LoanTransactionDetailCreate(
            loan_id=detail_kwargs.pop("loan_id", "LN-001"),
            principal=detail_kwargs.pop("principal", 8000.0),
            interest=detail_kwargs.pop("interest", 1200.0),
            excute_date=detail_kwargs.pop("excute_date", None),
            memo=detail_kwargs.pop("memo", None),
        ),
    )


def _rows(details: list[LoanJournal]) -> dict[str, float]:
    return {d.loan_excute_type: d.excute_price for d in details}


# ---------------------------------------------------------------- service ----


def test_happy_path_principal_and_interest(session: Session) -> None:
    _loan(session)
    j, details = create_journal_with_loan_transaction(session, _payload())

    assert j.distinct_number is not None
    assert j.spending == -9200.0
    assert j.action_main_type == "LoanRepayment"
    by_type = _rows(details)
    # Positive magnitudes, NOT a signed copy of journal.spending.
    assert by_type == {"principal": 8000.0, "interest": 1200.0}
    assert all(d.excute_date == "20260401" for d in details)  # defaulted from journal
    assert all(d.memo == "April payment" for d in details)


def test_principal_only_creates_one_row(session: Session) -> None:
    _loan(session)
    payload = _payload(
        journal_overrides={"spending": -5000.0}, principal=5000.0, interest=0.0
    )
    _, details = create_journal_with_loan_transaction(session, payload)
    assert _rows(details) == {"principal": 5000.0}


def test_interest_only_creates_one_row(session: Session) -> None:
    _loan(session)
    payload = _payload(
        journal_overrides={"spending": -300.0}, principal=0.0, interest=300.0
    )
    _, details = create_journal_with_loan_transaction(session, payload)
    assert _rows(details) == {"interest": 300.0}


def test_repayed_recalculated(session: Session) -> None:
    _loan(session, amount=250000.0)
    create_journal_with_loan_transaction(session, _payload(principal=8000.0, interest=1200.0))
    loan = session.get(Loan, "LN-001")
    assert loan.repayed == 8000.0  # cumulative principal only (interest excluded)


def test_sum_mismatch_rolls_back(session: Session) -> None:
    _loan(session)
    # spending magnitude 9000 != principal+interest 9200
    payload = _payload(journal_overrides={"spending": -9000.0}, principal=8000.0, interest=1200.0)
    with pytest.raises(HTTPException) as ei:
        create_journal_with_loan_transaction(session, payload)
    assert ei.value.status_code == 422

    session.rollback()
    assert session.exec(select(Journal)).first() is None
    assert session.exec(select(LoanJournal)).first() is None


def test_zero_total_rejected(session: Session) -> None:
    _loan(session)
    payload = _payload(journal_overrides={"spending": 0.0}, principal=0.0, interest=0.0)
    with pytest.raises(HTTPException) as ei:
        create_journal_with_loan_transaction(session, payload)
    assert ei.value.status_code == 422


def test_loan_not_found_rolls_back(session: Session) -> None:
    # No loan seeded — service should 404 before commit.
    payload = _payload(loan_id="LN-MISSING", journal_overrides={"action_sub": "LN-MISSING"})
    with pytest.raises(HTTPException) as ei:
        create_journal_with_loan_transaction(session, payload)
    assert ei.value.status_code == 404

    session.rollback()
    assert session.exec(select(Journal)).first() is None
    assert session.exec(select(LoanJournal)).first() is None


# ----------------------------------------------------- update composite ----


def _update_payload(
    *, journal_overrides: dict | None = None, **detail_kwargs
) -> JournalLoanTransactionUpdate:
    return JournalLoanTransactionUpdate(
        journal=JournalUpdate(**(journal_overrides or {})),
        loan_detail=LoanTransactionDetailCreate(
            loan_id=detail_kwargs.pop("loan_id", "LN-001"),
            principal=detail_kwargs.pop("principal", 8000.0),
            interest=detail_kwargs.pop("interest", 1200.0),
            excute_date=detail_kwargs.pop("excute_date", None),
            memo=detail_kwargs.pop("memo", None),
        ),
    )


def test_update_composite_happy_path(session: Session) -> None:
    """Edit a previously-untagged journal and create its Loan_Journal rows."""
    _loan(session)
    j = create_journal(
        session,
        JournalCreate(**_journal(action_sub=None, action_sub_type=None, action_sub_table=None, note="raw import")),
    )

    payload = _update_payload(
        journal_overrides={
            "action_sub": "LN-001",
            "action_sub_type": "Loan",
            "action_sub_table": "Loan",
            "note": "Re-classified as loan repayment",
        },
        principal=8000.0,
        interest=1200.0,
    )
    updated_j, details = update_journal_with_loan_transaction(session, j.distinct_number, payload)

    assert updated_j.distinct_number == j.distinct_number
    assert updated_j.note == "Re-classified as loan repayment"
    # Spending unchanged (not passed in the update) so it still matches 9200.
    assert updated_j.spending == -9200.0
    assert _rows(details) == {"principal": 8000.0, "interest": 1200.0}


# ----------------------------------------------------------------- router ----


def test_post_loan_transaction_endpoint_201(client: TestClient, session: Session) -> None:
    _loan(session)
    body = {
        "journal": _journal(),
        "loan_detail": {"loan_id": "LN-001", "principal": 8000.0, "interest": 1200.0},
    }
    r = client.post("/monthly-report/journals/loan-transaction", json=body)
    assert r.status_code == 201, r.text
    data = r.json()["data"]
    assert data["journal"]["spending"] == -9200.0
    by_type = {d["loan_excute_type"]: d["excute_price"] for d in data["loan_details"]}
    assert by_type == {"principal": 8000.0, "interest": 1200.0}


def test_post_loan_transaction_endpoint_422_mismatch(
    client: TestClient, session: Session
) -> None:
    _loan(session)
    body = {
        "journal": _journal(spending=-9000.0),
        "loan_detail": {"loan_id": "LN-001", "principal": 8000.0, "interest": 1200.0},
    }
    r = client.post("/monthly-report/journals/loan-transaction", json=body)
    assert r.status_code == 422, r.text
    assert session.exec(select(Journal)).first() is None


def test_post_loan_transaction_endpoint_422_negative_portion(
    client: TestClient, session: Session
) -> None:
    _loan(session)
    body = {
        "journal": _journal(spending=-8000.0),
        "loan_detail": {"loan_id": "LN-001", "principal": -8000.0, "interest": 0.0},
    }
    r = client.post("/monthly-report/journals/loan-transaction", json=body)
    assert r.status_code == 422, r.text  # rejected by ge=0 field constraint


def test_put_loan_transaction_endpoint_200(client: TestClient, session: Session) -> None:
    _loan(session)
    j = create_journal(session, JournalCreate(**_journal()))
    body = {
        "journal": {"note": "Re-tagged via PUT"},
        "loan_detail": {"loan_id": "LN-001", "principal": 8000.0, "interest": 1200.0},
    }
    r = client.put(
        f"/monthly-report/journals/{j.distinct_number}/loan-transaction", json=body
    )
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["journal"]["note"] == "Re-tagged via PUT"
    assert len(data["loan_details"]) == 2
