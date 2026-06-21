"""Composite endpoint: POST /monthly-report/journals/stock-transaction.

Covers the service-level transactional behaviour (sign preservation,
rollback on missing FK) and a router smoke pass.
"""
from __future__ import annotations

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.assets.stock import StockDetail, StockJournal, StockJournalCreate
from app.models.monthly_report.journal import Journal, JournalCreate, JournalUpdate
from app.models.monthly_report.journal_composite import (
    JournalStockTransactionCreate,
    JournalStockTransactionUpdate,
    StockTransactionDetailCreate,
)
from app.models.settings.account import Account, AccountCreate
from app.models.settings.credit_card import CreditCard, CreditCardCreate
from app.services.asset_service import create_stock
from app.services.monthly_report_service import (
    create_journal,
    create_journal_with_stock_transaction,
    update_journal_with_stock_transaction,
)
from app.services.setting_service import create_account, create_credit_card


# ---------------------------------------------------------------- helpers ----


def _account(session: Session, account_id: str = "BANK-CHASE-01") -> Account:
    return create_account(
        session,
        AccountCreate(
            account_id=account_id,
            name="Chase Checking",
            account_type="bank",
            fx_code="USD",
            is_calculate="Y",
            in_use="Y",
            discount=1.0,
            memo=None,
            owner="stone",
        ),
    )


def _credit_card(session: Session, credit_card_id: str = "CC-VISA-01") -> CreditCard:
    return create_credit_card(
        session,
        CreditCardCreate(
            credit_card_id=credit_card_id,
            card_name="Chase Sapphire",
            fx_code="USD",
            in_use="Y",
        ),
    )


def _holding(session: Session, stock_id: str = "STK-H-001") -> StockJournal:
    return create_stock(
        session,
        StockJournalCreate(
            stock_id=stock_id,
            stock_code="AAPL",
            stock_name="Apple Inc.",
            asset_id="AC-STK-001",
            expected_spend=10000.0,
        ),
    )


def _journal(**overrides) -> dict:
    base = {
        "vesting_month": "202604",
        "spend_date": "20260418",
        # PK of the account seeded by _account() — first insert in a fresh
        # session, so its autoincrement Account.id is 1.
        "spend_way": "1",
        "spend_way_type": "account",
        "spend_way_table": "Account",
        "action_main": "INV01",
        "action_main_type": "Invest",
        "action_main_table": "Code_Data",
        "action_sub": None,
        "action_sub_type": None,
        "action_sub_table": None,
        "spending": -1805.0,
        "invoice_number": None,
        "note": "Buy AAPL",
    }
    base.update(overrides)
    return base


def _payload(
    *, journal_overrides: dict | None = None, **detail_kwargs
) -> JournalStockTransactionCreate:
    return JournalStockTransactionCreate(
        journal=JournalCreate(**_journal(**(journal_overrides or {}))),
        stock_detail=StockTransactionDetailCreate(
            stock_id=detail_kwargs.pop("stock_id", "STK-H-001"),
            excute_type=detail_kwargs.pop("excute_type", "buy"),
            excute_amount=detail_kwargs.pop("excute_amount", 10.0),
            excute_date=detail_kwargs.pop("excute_date", None),
            memo=detail_kwargs.pop("memo", None),
        ),
    )


# ---------------------------------------------------------------- service ----


def test_happy_path_buy_preserves_negative_sign(session: Session) -> None:
    _account(session)
    _holding(session)
    j, d = create_journal_with_stock_transaction(session, _payload())

    assert j.distinct_number is not None
    assert d.distinct_number is not None
    assert j.spending == -1805.0
    # Signed pass-through: buy stays negative.
    assert d.excute_price == -1805.0
    assert d.excute_amount == 10.0
    assert d.excute_type == "buy"
    assert d.account_id == "BANK-CHASE-01"
    assert d.account_name == "Chase Checking"
    assert d.excute_date == "20260418"  # defaulted from journal.spend_date
    assert d.memo == "Buy AAPL"          # defaulted from journal.note


def test_happy_path_sell_preserves_positive_sign(session: Session) -> None:
    _account(session)
    _holding(session)
    payload = _payload(
        journal_overrides={"spending": 2100.0, "note": "Sell AAPL"},
        excute_type="sell",
        excute_amount=10.0,
    )
    j, d = create_journal_with_stock_transaction(session, payload)
    assert j.spending == 2100.0
    assert d.excute_price == 2100.0
    assert d.excute_type == "sell"


def test_cash_dividend_zero_amount(session: Session) -> None:
    _account(session)
    _holding(session)
    payload = _payload(
        journal_overrides={"spending": 25.0, "note": "AAPL dividend"},
        excute_type="cash",
        excute_amount=0.0,
    )
    j, d = create_journal_with_stock_transaction(session, payload)
    assert d.excute_type == "cash"
    assert d.excute_amount == 0.0
    assert d.excute_price == 25.0


def test_stock_dividend_zero_price(session: Session) -> None:
    _account(session)
    _holding(session)
    payload = _payload(
        journal_overrides={"spending": 0.0, "note": "Stock split 2:1"},
        excute_type="stock",
        excute_amount=10.0,
    )
    j, d = create_journal_with_stock_transaction(session, payload)
    assert d.excute_type == "stock"
    assert d.excute_amount == 10.0
    assert d.excute_price == 0.0


def test_cash_dividend_passive_income_positive_sign(session: Session) -> None:
    """A 股息 recorded as Passive income syncs to Stock_Detail, sign intact.

    This is the dividend-as-income contract the frontend relies on: the journal
    stays ``action_main_type='Passive'`` (so the income statement counts it as
    孳息) while the detail row carries the positive amount verbatim — the same
    composite endpoint used for buy/sell, with ``excute_type='cash'``.
    """
    _account(session)
    _holding(session)
    payload = _payload(
        journal_overrides={
            "action_main": "PAS01",
            "action_main_type": "Passive",
            "action_sub": "Stock",
            "action_sub_type": "Asset",
            "action_sub_table": "Stock_Detail",
            "spending": 25.0,
            "note": "AAPL cash dividend",
        },
        excute_type="cash",
        excute_amount=0.0,
    )
    j, d = create_journal_with_stock_transaction(session, payload)
    assert j.action_main_type == "Passive"
    assert j.spending == 25.0
    assert d.excute_type == "cash"
    assert d.excute_price == 25.0  # signed pass-through: income stays positive
    assert d.excute_amount == 0.0


def test_dividend_account_resolution_from_income_spend_way(session: Session) -> None:
    """An income journal's receiving account resolves like any other spend_way."""
    _account(session)
    _holding(session)
    payload = _payload(
        journal_overrides={
            "action_main_type": "Passive",
            "spending": 40.0,
            "note": "dividend into checking",
        },
        excute_type="cash",
        excute_amount=0.0,
    )
    _, d = create_journal_with_stock_transaction(session, payload)
    assert d.account_id == "BANK-CHASE-01"
    assert d.account_name == "Chase Checking"


@pytest.mark.parametrize("bad_spending", [-25.0, 0.0])
def test_cash_dividend_non_positive_rejected(session: Session, bad_spending: float) -> None:
    """A cash dividend must be a positive inflow; <=0 is rejected before commit.

    The income statement reads the *signed* journal amount, so a non-positive
    cash dividend would silently shrink 孳息 income — the service guard blocks it
    and nothing persists.
    """
    _account(session)
    _holding(session)
    payload = _payload(
        journal_overrides={
            "action_main_type": "Passive",
            "spending": bad_spending,
            "note": "wrong-signed dividend",
        },
        excute_type="cash",
        excute_amount=0.0,
    )
    with pytest.raises(HTTPException) as ei:
        create_journal_with_stock_transaction(session, payload)
    assert ei.value.status_code == 422

    session.rollback()  # mimic FastAPI dep teardown
    assert session.exec(select(Journal)).first() is None
    assert session.exec(select(StockDetail)).first() is None


def test_holding_not_found_rolls_back(session: Session) -> None:
    _account(session)
    # No holding seeded — service should 404 before commit.
    payload = _payload(stock_id="STK-MISSING")
    with pytest.raises(HTTPException) as ei:
        create_journal_with_stock_transaction(session, payload)
    assert ei.value.status_code == 404

    session.rollback()  # mimic FastAPI dep teardown
    assert session.exec(select(Journal)).first() is None
    assert session.exec(select(StockDetail)).first() is None


def test_account_not_found_rolls_back(session: Session) -> None:
    _holding(session)  # holding exists, but no account
    payload = _payload()
    with pytest.raises(HTTPException) as ei:
        create_journal_with_stock_transaction(session, payload)
    assert ei.value.status_code == 404

    session.rollback()
    assert session.exec(select(Journal)).first() is None


def test_credit_card_payment_allowed(session: Session) -> None:
    """Credit-card-funded stock purchases are accepted (e.g. brokerage on CC).

    The Stock_Detail row records the credit card as the settling source so the
    holding history stays traceable.
    """
    _credit_card(session)
    _holding(session)
    payload = _payload(
        journal_overrides={
            "spend_way": "CC-VISA-01",
            "spend_way_type": "credit_card",
            "spend_way_table": "Credit_Card",
        }
    )
    j, d = create_journal_with_stock_transaction(session, payload)
    assert j.spend_way == "CC-VISA-01"
    assert d.account_id == "CC-VISA-01"
    assert d.account_name == "Chase Sapphire"
    assert d.excute_price == -1805.0


def test_credit_card_not_found_rolls_back(session: Session) -> None:
    _holding(session)  # no credit card seeded
    payload = _payload(
        journal_overrides={
            "spend_way": "CC-MISSING",
            "spend_way_type": "credit_card",
            "spend_way_table": "Credit_Card",
        }
    )
    with pytest.raises(HTTPException) as ei:
        create_journal_with_stock_transaction(session, payload)
    assert ei.value.status_code == 404

    session.rollback()
    assert session.exec(select(Journal)).first() is None


def test_explicit_date_and_memo_override_defaults(session: Session) -> None:
    _account(session)
    _holding(session)
    payload = _payload(
        excute_date="20260101",
        memo="custom memo",
    )
    _, d = create_journal_with_stock_transaction(session, payload)
    assert d.excute_date == "20260101"
    assert d.memo == "custom memo"


# ----------------------------------------------------------------- router ----


def test_post_stock_transaction_endpoint_201(client: TestClient, session: Session) -> None:
    _account(session)
    _holding(session)
    body = {
        "journal": _journal(),
        "stock_detail": {
            "stock_id": "STK-H-001",
            "excute_type": "buy",
            "excute_amount": 10.0,
        },
    }
    r = client.post("/monthly-report/journals/stock-transaction", json=body)
    assert r.status_code == 201, r.text
    data = r.json()["data"]
    assert data["journal"]["spending"] == -1805.0
    assert data["stock_detail"]["excute_price"] == -1805.0
    assert data["stock_detail"]["stock_id"] == "STK-H-001"


def test_post_stock_transaction_endpoint_404_missing_holding(
    client: TestClient, session: Session
) -> None:
    _account(session)  # no holding
    body = {
        "journal": _journal(),
        "stock_detail": {
            "stock_id": "STK-MISSING",
            "excute_type": "buy",
            "excute_amount": 1.0,
        },
    }
    r = client.post("/monthly-report/journals/stock-transaction", json=body)
    assert r.status_code == 404
    # Regression-style check: no Journal should have leaked into the DB.
    assert session.exec(select(Journal)).first() is None


def test_post_stock_transaction_endpoint_422_non_positive_cash_dividend(
    client: TestClient, session: Session
) -> None:
    _account(session)
    _holding(session)
    body = {
        "journal": _journal(action_main_type="Passive", spending=-25.0, note="bad dividend"),
        "stock_detail": {
            "stock_id": "STK-H-001",
            "excute_type": "cash",
            "excute_amount": 0.0,
        },
    }
    r = client.post("/monthly-report/journals/stock-transaction", json=body)
    assert r.status_code == 422, r.text
    assert session.exec(select(Journal)).first() is None


def test_existing_plain_journal_post_still_works(client: TestClient) -> None:
    # Regression smoke: the composite route is added without disturbing the
    # original Journal POST contract.
    r = client.post("/monthly-report/journals", json=_journal())
    assert r.status_code == 201


# ----------------------------------------------------- update composite ----


def _update_payload(
    *, journal_overrides: dict | None = None, **detail_kwargs
) -> JournalStockTransactionUpdate:
    return JournalStockTransactionUpdate(
        journal=JournalUpdate(**(journal_overrides or {})),
        stock_detail=StockTransactionDetailCreate(
            stock_id=detail_kwargs.pop("stock_id", "STK-H-001"),
            excute_type=detail_kwargs.pop("excute_type", "buy"),
            excute_amount=detail_kwargs.pop("excute_amount", 10.0),
            excute_date=detail_kwargs.pop("excute_date", None),
            memo=detail_kwargs.pop("memo", None),
        ),
    )


def test_update_composite_happy_path(session: Session) -> None:
    """Edit a previously-untagged journal and create its first Stock_Detail atomically."""
    _account(session)
    _holding(session)
    j = create_journal(session, JournalCreate(**_journal(spending=-1700.0, note="raw import")))

    payload = _update_payload(
        journal_overrides={
            "action_sub": "Stock",
            "action_sub_type": "Asset",
            "action_sub_table": "Stock_Detail",
            "note": "Re-classified as AAPL buy",
        },
        excute_amount=5.0,
    )
    updated_j, d = update_journal_with_stock_transaction(session, j.distinct_number, payload)

    assert updated_j.distinct_number == j.distinct_number
    assert updated_j.action_sub == "Stock"
    assert updated_j.note == "Re-classified as AAPL buy"
    # Spending unchanged because we did not pass it in the update.
    assert updated_j.spending == -1700.0
    assert d.excute_price == -1700.0
    assert d.excute_amount == 5.0
    assert d.stock_id == "STK-H-001"


def test_update_composite_missing_journal(session: Session) -> None:
    _account(session)
    _holding(session)
    payload = _update_payload(journal_overrides={"note": "ghost"})
    with pytest.raises(HTTPException) as ei:
        update_journal_with_stock_transaction(session, 99999, payload)
    assert ei.value.status_code == 404


def test_update_composite_missing_holding_rolls_back(session: Session) -> None:
    _account(session)
    _holding(session)
    j = create_journal(session, JournalCreate(**_journal()))
    original_note = j.note

    payload = _update_payload(stock_id="STK-MISSING", journal_overrides={"note": "should not stick"})
    with pytest.raises(HTTPException) as ei:
        update_journal_with_stock_transaction(session, j.distinct_number, payload)
    assert ei.value.status_code == 404

    session.rollback()
    session.expire_all()
    refreshed = session.get(Journal, j.distinct_number)
    assert refreshed is not None
    # Rollback discards the in-flight note change.
    assert refreshed.note == original_note
    assert session.exec(select(StockDetail)).first() is None


def test_put_composite_endpoint_200(client: TestClient, session: Session) -> None:
    _account(session)
    _holding(session)
    j = create_journal(session, JournalCreate(**_journal()))
    body = {
        "journal": {"note": "Re-tagged via PUT"},
        "stock_detail": {
            "stock_id": "STK-H-001",
            "excute_type": "buy",
            "excute_amount": 7.0,
        },
    }
    r = client.put(
        f"/monthly-report/journals/{j.distinct_number}/stock-transaction", json=body
    )
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["journal"]["note"] == "Re-tagged via PUT"
    assert data["stock_detail"]["excute_amount"] == 7.0
    assert data["stock_detail"]["excute_price"] == -1805.0
