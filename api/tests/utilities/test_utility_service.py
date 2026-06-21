"""Service-layer tests for utility selection groups."""
from __future__ import annotations

import pytest
from fastapi import HTTPException
from sqlmodel import Session

from app.models.assets.insurance import Insurance
from app.models.assets.loan import Loan
from app.models.assets.stock_category import StockCategory
from app.models.settings.account import Account
from app.models.settings.code_data import CodeData
from app.models.settings.credit_card import CreditCard
from app.services.utility_service import (
    get_account_selection_groups,
    get_code_selection_groups,
    get_credit_card_selection_groups,
    get_insurance_selection_groups,
    get_loan_selection_groups,
    get_stock_category_selection_groups,
    get_sub_code_selection_groups,
)


def _make_account(**overrides) -> Account:
    base = dict(
        account_id="AC1",
        name="Cash NTD",
        account_type="CASH",
        fx_code="TWD",
        is_calculate="Y",
        in_use="Y",
        discount=1.0,
        owner=None,
        memo=None,
        account_index=1,
    )
    base.update(overrides)
    return Account(**base)


def test_get_account_selection_groups(session: Session) -> None:
    session.add(_make_account(account_id="A1", name="Cash NTD", account_type="CASH", account_index=1))
    session.add(_make_account(account_id="A2", name="Savings", account_type="BANK", account_index=2))
    session.add(_make_account(account_id="A3", name="Wallet", account_type="CASH", account_index=3))
    session.add(_make_account(account_id="A4", name="Inactive", account_type="BANK", account_index=4, in_use="N"))
    session.commit()

    groups = get_account_selection_groups(session)
    # Same account_type is consolidated into a single group regardless of
    # interleaved indexes. Group order follows first-seen account_type
    # (CASH appears at index 1 → first; BANK at index 2 → second).
    assert [g.label for g in groups] == ["CASH", "BANK"]
    assert [o.label for o in groups[0].options] == ["Cash NTD", "Wallet"]
    assert [o.label for o in groups[1].options] == ["Savings"]
    # values are stringified ids
    assert all(isinstance(o.value, str) for g in groups for o in g.options)


def test_get_credit_card_selection_groups(session: Session) -> None:
    assert get_credit_card_selection_groups(session) == []

    session.add(
        CreditCard(
            credit_card_id="CC1",
            card_name="Visa A",
            fx_code="TWD",
            in_use="Y",
            credit_card_index=1,
        )
    )
    session.add(
        CreditCard(
            credit_card_id="CC2",
            card_name="Visa B",
            fx_code="TWD",
            in_use="N",
            credit_card_index=2,
        )
    )
    session.commit()

    groups = get_credit_card_selection_groups(session)
    assert len(groups) == 1
    assert groups[0].label == "Credit_Card"
    assert [o.value for o in groups[0].options] == ["CC1"]
    assert [o.label for o in groups[0].options] == ["Visa A"]


def test_get_loan_selection_groups(session: Session) -> None:
    assert get_loan_selection_groups(session) == []

    session.add(
        Loan(
            loan_id="LN1",
            loan_name="Mortgage",
            loan_type="mortgage",
            account_id="AC1",
            account_name="Bank",
            interest_rate=0.03,
            period=240,
            apply_date="20200101",
            grace_expire_date=None,
            pay_day=1,
            amount=1000.0,
            repayed=0.0,
            loan_index=1,
        )
    )
    session.commit()

    groups = get_loan_selection_groups(session)
    assert len(groups) == 1
    assert groups[0].label == "Loan"
    assert groups[0].options[0].value == "LN1"
    assert groups[0].options[0].label == "Mortgage"


def test_get_insurance_selection_groups(session: Session) -> None:
    assert get_insurance_selection_groups(session) == []

    session.add(
        Insurance(
            insurance_id="INS1",
            insurance_name="Life",
            asset_id="AS1",
            in_account="AC1",
            out_account="AC1",
            start_date="20200101",
            end_date="20500101",
            pay_type="annual",
            pay_day="01",
            expected_spend=1000.0,
            has_closed="N",
        )
    )
    session.add(
        Insurance(
            insurance_id="INS2",
            insurance_name="Closed",
            asset_id="AS1",
            in_account="AC1",
            out_account="AC1",
            start_date="20200101",
            end_date="20210101",
            pay_type="annual",
            pay_day="01",
            expected_spend=0.0,
            has_closed="Y",
        )
    )
    session.commit()

    groups = get_insurance_selection_groups(session)
    assert len(groups) == 1
    assert groups[0].label == "Insurance"
    assert [o.value for o in groups[0].options] == ["INS1"]


def test_get_stock_category_selection_groups(session: Session) -> None:
    assert get_stock_category_selection_groups(session) == []

    session.add(StockCategory(category_id="SC-001", name="成長型", in_use="Y", category_index=2))
    session.add(StockCategory(category_id="SC-002", name="債券", in_use="Y", category_index=1))
    session.add(StockCategory(category_id="SC-003", name="停用", in_use="N", category_index=3))
    session.commit()

    groups = get_stock_category_selection_groups(session)
    assert len(groups) == 1
    assert groups[0].label == "Stock_Category"
    # Ordered by category_index (債券=1 before 成長型=2); inactive excluded.
    assert [o.value for o in groups[0].options] == ["SC-002", "SC-001"]
    assert [o.label for o in groups[0].options] == ["債券", "成長型"]


def _make_code(**overrides) -> CodeData:
    base = dict(
        code_id="C1",
        code_type="Floating",
        name="Food",
        parent_id=None,
        in_use="Y",
        code_index=1,
    )
    base.update(overrides)
    return CodeData(**base)


def test_get_code_selection_groups(session: Session) -> None:
    session.add(_make_code(code_id="MAIN-A", code_type="Floating", name="Food", code_index=1))
    session.add(_make_code(code_id="MAIN-B", code_type="Income", name="Salary", code_index=2))
    session.add(_make_code(code_id="SUB-A", code_type="Floating", name="Groceries", parent_id="MAIN-A", code_index=3))
    session.add(_make_code(code_id="MAIN-OFF", code_type="Floating", name="Off", in_use="N", code_index=4))
    session.commit()

    groups = get_code_selection_groups(session)
    by_label = {g.label: g for g in groups}
    assert set(by_label.keys()) == {"Floating", "Income"}
    assert [o.value for o in by_label["Floating"].options] == ["MAIN-A"]
    assert [o.value for o in by_label["Income"].options] == ["MAIN-B"]


def test_get_sub_code_selection_groups(session: Session) -> None:
    session.add(_make_code(code_id="MAIN-A", code_type="Floating", name="Food", code_index=1))
    session.add(_make_code(code_id="SUB-1", code_type="Floating", name="Groceries", parent_id="MAIN-A", code_index=2))
    session.add(_make_code(code_id="SUB-2", code_type="Floating", name="Eating Out", parent_id="MAIN-A", code_index=3))
    session.add(_make_code(code_id="SUB-OFF", code_type="Floating", name="Off", parent_id="MAIN-A", in_use="N", code_index=4))
    session.commit()

    groups = get_sub_code_selection_groups(session, "MAIN-A")
    assert len(groups) == 1
    assert groups[0].label == "sub"
    assert [o.value for o in groups[0].options] == ["SUB-1", "SUB-2"]

    with pytest.raises(HTTPException) as exc:
        get_sub_code_selection_groups(session, "UNKNOWN")
    assert exc.value.status_code == 404
