"""Composite endpoint: POST /monthly-report/journals/estate-transaction.

Mirrors test_journal_stock_transaction.py. Covers the service-level
transactional behaviour (signed pass-through into excute_price, rollback on
missing FK) and a router smoke pass.

Divergence from the stock suite: Estate_Journal has no account columns, so
there is no settling-source lookup — funding the expense from any spend_way
(account *or* credit card) is accepted and nothing is stored about it.
"""
from __future__ import annotations

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.assets.estate import Estate, EstateCreate, EstateJournal
from app.models.monthly_report.journal import Journal, JournalCreate, JournalUpdate
from app.models.monthly_report.journal_composite import (
    EstateTransactionDetailCreate,
    JournalEstateTransactionCreate,
    JournalEstateTransactionUpdate,
)
from app.services.asset_service import create_estate
from app.services.monthly_report_service import (
    create_journal,
    create_journal_with_estate_transaction,
    update_journal_with_estate_transaction,
)


# ---------------------------------------------------------------- helpers ----


def _estate(session: Session, estate_id: str = "EST-001") -> Estate:
    return create_estate(
        session,
        EstateCreate(
            estate_id=estate_id,
            estate_name="Condo",
            estate_type="residential",
            estate_address="123 Main St",
            asset_id="AC-REAL-001",
            obtain_date="20200101",
            loan_id=None,
            estate_status="live",
            memo="Primary residence",
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
        "action_sub": "Estate",
        "action_sub_type": "Asset",
        "action_sub_table": "Estate_Journal",
        "spending": -8000.0,
        "invoice_number": None,
        "note": "Property tax",
    }
    base.update(overrides)
    return base


def _payload(
    *, journal_overrides: dict | None = None, **detail_kwargs
) -> JournalEstateTransactionCreate:
    return JournalEstateTransactionCreate(
        journal=JournalCreate(**_journal(**(journal_overrides or {}))),
        estate_detail=EstateTransactionDetailCreate(
            estate_id=detail_kwargs.pop("estate_id", "EST-001"),
            estate_excute_type=detail_kwargs.pop("estate_excute_type", "tax"),
            excute_date=detail_kwargs.pop("excute_date", None),
            memo=detail_kwargs.pop("memo", None),
        ),
    )


# ---------------------------------------------------------------- service ----


def test_happy_path_tax_preserves_negative_sign(session: Session) -> None:
    _estate(session)
    j, d = create_journal_with_estate_transaction(session, _payload())

    assert j.distinct_number is not None
    assert d.distinct_number is not None
    assert j.spending == -8000.0
    # Signed pass-through: tax/outflow stays negative.
    assert d.excute_price == -8000.0
    assert d.estate_excute_type == "tax"
    assert d.estate_id == "EST-001"
    assert d.excute_date == "20260115"  # defaulted from journal.spend_date
    assert d.memo == "Property tax"     # defaulted from journal.note


def test_happy_path_rent_preserves_positive_sign(session: Session) -> None:
    _estate(session)
    payload = _payload(
        journal_overrides={"spending": 15000.0, "note": "Rent received"},
        estate_excute_type="rent",
    )
    j, d = create_journal_with_estate_transaction(session, payload)
    assert j.spending == 15000.0
    assert d.excute_price == 15000.0
    assert d.estate_excute_type == "rent"


def test_estate_not_found_rolls_back(session: Session) -> None:
    # No estate seeded — service should 404 before commit.
    payload = _payload(estate_id="EST-MISSING")
    with pytest.raises(HTTPException) as ei:
        create_journal_with_estate_transaction(session, payload)
    assert ei.value.status_code == 404

    session.rollback()  # mimic FastAPI dep teardown
    assert session.exec(select(Journal)).first() is None
    assert session.exec(select(EstateJournal)).first() is None


def test_credit_card_funded_allowed(session: Session) -> None:
    """Credit-card-funded estate expenses are accepted: no settling-source guard."""
    _estate(session)
    payload = _payload(
        journal_overrides={
            "spend_way": "CC-VISA-01",
            "spend_way_type": "credit_card",
            "spend_way_table": "Credit_Card",
        }
    )
    j, d = create_journal_with_estate_transaction(session, payload)
    assert j.spend_way == "CC-VISA-01"
    assert d.excute_price == -8000.0


def test_explicit_date_and_memo_override_defaults(session: Session) -> None:
    _estate(session)
    payload = _payload(excute_date="20260101", memo="custom memo")
    _, d = create_journal_with_estate_transaction(session, payload)
    assert d.excute_date == "20260101"
    assert d.memo == "custom memo"


# ----------------------------------------------------------------- router ----


def test_post_estate_transaction_endpoint_201(
    client: TestClient, session: Session
) -> None:
    _estate(session)
    body = {
        "journal": _journal(),
        "estate_detail": {
            "estate_id": "EST-001",
            "estate_excute_type": "tax",
        },
    }
    r = client.post("/monthly-report/journals/estate-transaction", json=body)
    assert r.status_code == 201, r.text
    data = r.json()["data"]
    assert data["journal"]["spending"] == -8000.0
    assert data["estate_detail"]["excute_price"] == -8000.0
    assert data["estate_detail"]["estate_id"] == "EST-001"


def test_post_estate_transaction_endpoint_404_missing_estate(
    client: TestClient, session: Session
) -> None:
    body = {
        "journal": _journal(),
        "estate_detail": {
            "estate_id": "EST-MISSING",
            "estate_excute_type": "tax",
        },
    }
    r = client.post("/monthly-report/journals/estate-transaction", json=body)
    assert r.status_code == 404
    assert session.exec(select(Journal)).first() is None


# ----------------------------------------------------- update composite ----


def _update_payload(
    *, journal_overrides: dict | None = None, **detail_kwargs
) -> JournalEstateTransactionUpdate:
    return JournalEstateTransactionUpdate(
        journal=JournalUpdate(**(journal_overrides or {})),
        estate_detail=EstateTransactionDetailCreate(
            estate_id=detail_kwargs.pop("estate_id", "EST-001"),
            estate_excute_type=detail_kwargs.pop("estate_excute_type", "tax"),
            excute_date=detail_kwargs.pop("excute_date", None),
            memo=detail_kwargs.pop("memo", None),
        ),
    )


def test_update_composite_happy_path(session: Session) -> None:
    """Edit a previously-untagged journal and create its first Estate_Journal."""
    _estate(session)
    j = create_journal(
        session,
        JournalCreate(
            **_journal(
                spending=-7000.0,
                note="raw import",
                action_sub=None,
                action_sub_type=None,
                action_sub_table=None,
            )
        ),
    )

    payload = _update_payload(
        journal_overrides={
            "action_sub": "Estate",
            "action_sub_type": "Asset",
            "action_sub_table": "Estate_Journal",
            "note": "Re-classified as property tax",
        },
    )
    updated_j, d = update_journal_with_estate_transaction(
        session, j.distinct_number, payload
    )

    assert updated_j.distinct_number == j.distinct_number
    assert updated_j.action_sub == "Estate"
    assert updated_j.note == "Re-classified as property tax"
    # Spending unchanged because we did not pass it in the update.
    assert updated_j.spending == -7000.0
    assert d.excute_price == -7000.0
    assert d.estate_id == "EST-001"


def test_update_composite_missing_journal(session: Session) -> None:
    _estate(session)
    payload = _update_payload(journal_overrides={"note": "ghost"})
    with pytest.raises(HTTPException) as ei:
        update_journal_with_estate_transaction(session, 99999, payload)
    assert ei.value.status_code == 404


def test_update_composite_missing_estate_rolls_back(session: Session) -> None:
    _estate(session)
    j = create_journal(session, JournalCreate(**_journal()))
    original_note = j.note

    payload = _update_payload(
        estate_id="EST-MISSING", journal_overrides={"note": "should not stick"}
    )
    with pytest.raises(HTTPException) as ei:
        update_journal_with_estate_transaction(session, j.distinct_number, payload)
    assert ei.value.status_code == 404

    session.rollback()
    session.expire_all()
    refreshed = session.get(Journal, j.distinct_number)
    assert refreshed is not None
    assert refreshed.note == original_note
    assert session.exec(select(EstateJournal)).first() is None


def test_put_composite_endpoint_200(client: TestClient, session: Session) -> None:
    _estate(session)
    j = create_journal(session, JournalCreate(**_journal()))
    body = {
        "journal": {"note": "Re-tagged via PUT"},
        "estate_detail": {
            "estate_id": "EST-001",
            "estate_excute_type": "tax",
        },
    }
    r = client.put(
        f"/monthly-report/journals/{j.distinct_number}/estate-transaction", json=body
    )
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["journal"]["note"] == "Re-tagged via PUT"
    assert data["estate_detail"]["excute_price"] == -8000.0
