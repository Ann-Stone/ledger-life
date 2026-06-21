"""Composite endpoint: POST /monthly-report/journals/insurance-transaction.

Mirrors test_journal_stock_transaction.py. Covers the service-level
transactional behaviour (signed pass-through into excute_price, rollback on
missing FK) and a router smoke pass.

Divergence from the stock suite: Insurance_Journal has no account columns, so
there is no settling-source lookup — funding the premium from any spend_way
(account *or* credit card) is accepted and nothing is stored about it.
"""
from __future__ import annotations

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.assets.insurance import Insurance, InsuranceCreate, InsuranceJournal
from app.models.monthly_report.journal import Journal, JournalCreate, JournalUpdate
from app.models.monthly_report.journal_composite import (
    InsuranceTransactionDetailCreate,
    JournalInsuranceTransactionCreate,
    JournalInsuranceTransactionUpdate,
)
from app.services.asset_service import create_insurance
from app.services.monthly_report_service import (
    create_journal,
    create_journal_with_insurance_transaction,
    update_journal_with_insurance_transaction,
)


# ---------------------------------------------------------------- helpers ----


def _policy(session: Session, insurance_id: str = "INS-001") -> Insurance:
    return create_insurance(
        session,
        InsuranceCreate(
            insurance_id=insurance_id,
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
        ),
    )


def _journal(**overrides) -> dict:
    base = {
        "vesting_month": "202601",
        "spend_date": "20260115",
        "spend_way": "1",
        "spend_way_type": "account",
        "spend_way_table": "Account",
        "action_main": "TRA",
        "action_main_type": "Transfer",
        "action_main_table": "Code_Data",
        "action_sub": "Insurance",
        "action_sub_type": "Asset",
        "action_sub_table": "Insurance_Journal",
        "spending": -1200.0,
        "invoice_number": None,
        "note": "Annual premium",
    }
    base.update(overrides)
    return base


def _payload(
    *, journal_overrides: dict | None = None, **detail_kwargs
) -> JournalInsuranceTransactionCreate:
    return JournalInsuranceTransactionCreate(
        journal=JournalCreate(**_journal(**(journal_overrides or {}))),
        insurance_detail=InsuranceTransactionDetailCreate(
            insurance_id=detail_kwargs.pop("insurance_id", "INS-001"),
            insurance_excute_type=detail_kwargs.pop("insurance_excute_type", "pay"),
            excute_date=detail_kwargs.pop("excute_date", None),
            memo=detail_kwargs.pop("memo", None),
        ),
    )


# ---------------------------------------------------------------- service ----


def test_happy_path_pay_preserves_negative_sign(session: Session) -> None:
    _policy(session)
    j, d = create_journal_with_insurance_transaction(session, _payload())

    assert j.distinct_number is not None
    assert d.distinct_number is not None
    assert j.spending == -1200.0
    # Signed pass-through: premium/outflow stays negative.
    assert d.excute_price == -1200.0
    assert d.insurance_excute_type == "pay"
    assert d.insurance_id == "INS-001"
    assert d.excute_date == "20260115"  # defaulted from journal.spend_date
    assert d.memo == "Annual premium"   # defaulted from journal.note


def test_happy_path_refund_preserves_positive_sign(session: Session) -> None:
    _policy(session)
    payload = _payload(
        journal_overrides={"spending": 500.0, "note": "Policy refund"},
        insurance_excute_type="return",
    )
    j, d = create_journal_with_insurance_transaction(session, payload)
    assert j.spending == 500.0
    assert d.excute_price == 500.0
    assert d.insurance_excute_type == "return"


def test_policy_not_found_rolls_back(session: Session) -> None:
    # No policy seeded — service should 404 before commit.
    payload = _payload(insurance_id="INS-MISSING")
    with pytest.raises(HTTPException) as ei:
        create_journal_with_insurance_transaction(session, payload)
    assert ei.value.status_code == 404

    session.rollback()  # mimic FastAPI dep teardown
    assert session.exec(select(Journal)).first() is None
    assert session.exec(select(InsuranceJournal)).first() is None


def test_credit_card_funded_allowed(session: Session) -> None:
    """Credit-card-funded premiums are accepted: no settling-source guard exists."""
    _policy(session)
    payload = _payload(
        journal_overrides={
            "spend_way": "CC-VISA-01",
            "spend_way_type": "credit_card",
            "spend_way_table": "Credit_Card",
        }
    )
    j, d = create_journal_with_insurance_transaction(session, payload)
    assert j.spend_way == "CC-VISA-01"
    assert d.excute_price == -1200.0


def test_explicit_date_and_memo_override_defaults(session: Session) -> None:
    _policy(session)
    payload = _payload(excute_date="20260101", memo="custom memo")
    _, d = create_journal_with_insurance_transaction(session, payload)
    assert d.excute_date == "20260101"
    assert d.memo == "custom memo"


# ----------------------------------------------------------------- router ----


def test_post_insurance_transaction_endpoint_201(
    client: TestClient, session: Session
) -> None:
    _policy(session)
    body = {
        "journal": _journal(),
        "insurance_detail": {
            "insurance_id": "INS-001",
            "insurance_excute_type": "pay",
        },
    }
    r = client.post("/monthly-report/journals/insurance-transaction", json=body)
    assert r.status_code == 201, r.text
    data = r.json()["data"]
    assert data["journal"]["spending"] == -1200.0
    assert data["insurance_detail"]["excute_price"] == -1200.0
    assert data["insurance_detail"]["insurance_id"] == "INS-001"


def test_post_insurance_transaction_endpoint_404_missing_policy(
    client: TestClient, session: Session
) -> None:
    body = {
        "journal": _journal(),
        "insurance_detail": {
            "insurance_id": "INS-MISSING",
            "insurance_excute_type": "pay",
        },
    }
    r = client.post("/monthly-report/journals/insurance-transaction", json=body)
    assert r.status_code == 404
    assert session.exec(select(Journal)).first() is None


# ----------------------------------------------------- update composite ----


def _update_payload(
    *, journal_overrides: dict | None = None, **detail_kwargs
) -> JournalInsuranceTransactionUpdate:
    return JournalInsuranceTransactionUpdate(
        journal=JournalUpdate(**(journal_overrides or {})),
        insurance_detail=InsuranceTransactionDetailCreate(
            insurance_id=detail_kwargs.pop("insurance_id", "INS-001"),
            insurance_excute_type=detail_kwargs.pop("insurance_excute_type", "pay"),
            excute_date=detail_kwargs.pop("excute_date", None),
            memo=detail_kwargs.pop("memo", None),
        ),
    )


def test_update_composite_happy_path(session: Session) -> None:
    """Edit a previously-untagged journal and create its first Insurance_Journal."""
    _policy(session)
    j = create_journal(
        session,
        JournalCreate(
            **_journal(
                spending=-1100.0,
                note="raw import",
                action_sub=None,
                action_sub_type=None,
                action_sub_table=None,
            )
        ),
    )

    payload = _update_payload(
        journal_overrides={
            "action_sub": "Insurance",
            "action_sub_type": "Asset",
            "action_sub_table": "Insurance_Journal",
            "note": "Re-classified as premium",
        },
    )
    updated_j, d = update_journal_with_insurance_transaction(
        session, j.distinct_number, payload
    )

    assert updated_j.distinct_number == j.distinct_number
    assert updated_j.action_sub == "Insurance"
    assert updated_j.note == "Re-classified as premium"
    # Spending unchanged because we did not pass it in the update.
    assert updated_j.spending == -1100.0
    assert d.excute_price == -1100.0
    assert d.insurance_id == "INS-001"


def test_update_composite_missing_journal(session: Session) -> None:
    _policy(session)
    payload = _update_payload(journal_overrides={"note": "ghost"})
    with pytest.raises(HTTPException) as ei:
        update_journal_with_insurance_transaction(session, 99999, payload)
    assert ei.value.status_code == 404


def test_update_composite_missing_policy_rolls_back(session: Session) -> None:
    _policy(session)
    j = create_journal(session, JournalCreate(**_journal()))
    original_note = j.note

    payload = _update_payload(
        insurance_id="INS-MISSING", journal_overrides={"note": "should not stick"}
    )
    with pytest.raises(HTTPException) as ei:
        update_journal_with_insurance_transaction(session, j.distinct_number, payload)
    assert ei.value.status_code == 404

    session.rollback()
    session.expire_all()
    refreshed = session.get(Journal, j.distinct_number)
    assert refreshed is not None
    assert refreshed.note == original_note
    assert session.exec(select(InsuranceJournal)).first() is None


def test_put_composite_endpoint_200(client: TestClient, session: Session) -> None:
    _policy(session)
    j = create_journal(session, JournalCreate(**_journal()))
    body = {
        "journal": {"note": "Re-tagged via PUT"},
        "insurance_detail": {
            "insurance_id": "INS-001",
            "insurance_excute_type": "pay",
        },
    }
    r = client.put(
        f"/monthly-report/journals/{j.distinct_number}/insurance-transaction", json=body
    )
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["journal"]["note"] == "Re-tagged via PUT"
    assert data["insurance_detail"]["excute_price"] == -1200.0
