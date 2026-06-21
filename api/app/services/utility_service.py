"""Utility domain service functions — dropdown selection groups."""
from __future__ import annotations


from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.assets.estate import Estate
from app.models.assets.insurance import Insurance
from app.models.assets.loan import Loan
from app.models.assets.other_asset import OtherAsset
from app.models.assets.stock import StockJournal
from app.models.assets.stock_category import StockCategory
from app.models.settings.account import Account
from app.models.settings.code_data import CodeData
from app.models.settings.credit_card import CreditCard
from app.models.utilities.selection import SelectionGroup, SelectionOption


def get_account_selection_groups(session: Session) -> list[SelectionGroup]:
    """Active accounts consolidated into one group per account_type.

    Rows are queried ordered by account_index so options inside each group
    follow that order; group order is the first-seen account_type.

    The option value is the autoincrement PK ``Account.id`` (stringified) —
    Journal.spend_way references the account by its primary key, the same way
    a credit-card journal references ``Credit_Card.credit_card_id`` (also a PK).
    Backend lookups (``compute_gain_loss``, settlement, composite endpoints)
    resolve spend_way against ``Account.id`` to stay symmetric across both
    payment-source tables.
    """
    rows = session.exec(
        select(Account)
        .where(Account.in_use == "Y")
        .order_by(Account.account_index.asc(), Account.id.asc())
    ).all()
    grouped: dict[str, list[Account]] = {}
    for a in rows:
        grouped.setdefault(a.account_type, []).append(a)
    return [
        SelectionGroup(
            label=key,
            options=[SelectionOption(value=str(a.id), label=a.name) for a in items],
        )
        for key, items in grouped.items()
    ]


def get_credit_card_selection_groups(session: Session) -> list[SelectionGroup]:
    """Active credit cards as a single group labelled 'Credit_Card'."""
    rows = session.exec(
        select(CreditCard)
        .where(CreditCard.in_use == "Y")
        .order_by(CreditCard.credit_card_index.asc(), CreditCard.credit_card_id.asc())
    ).all()
    if not rows:
        return []
    return [
        SelectionGroup(
            label="Credit_Card",
            options=[
                SelectionOption(value=c.credit_card_id, label=c.card_name) for c in rows
            ],
        )
    ]


def get_loan_selection_groups(session: Session) -> list[SelectionGroup]:
    """Active loans as a single group labelled 'Loan'.

    Loan has no `in_use` column; legacy semantics treat all rows as active. The
    granular ticket text uses `in_use == "Y"` as a placeholder; we degrade to
    "all loans, ordered by loan_index" to match the actual model.
    """
    rows = session.exec(
        select(Loan).order_by(Loan.loan_index.asc(), Loan.loan_id.asc())
    ).all()
    if not rows:
        return []
    return [
        SelectionGroup(
            label="Loan",
            options=[SelectionOption(value=l.loan_id, label=l.loan_name) for l in rows],
        )
    ]


def get_other_asset_type_selection_groups(session: Session) -> list[SelectionGroup]:
    """Distinct asset_type values from active Other_Asset rows, one group.

    Frontend uses this to drive the "transfer to other asset" sub-category
    dropdown, so it stays in sync with whatever asset categories the user has
    set up in `/setting`. Labels mirror the values verbatim; presentation
    translation (e.g. "stock" → "股票") happens client-side via the existing
    selection-label map.
    """
    rows = session.exec(
        select(OtherAsset)
        .where(OtherAsset.in_use == "Y")
        .order_by(OtherAsset.asset_index.asc(), OtherAsset.asset_id.asc())
    ).all()
    seen: set[str] = set()
    options: list[SelectionOption] = []
    for r in rows:
        if r.asset_type in seen:
            continue
        seen.add(r.asset_type)
        options.append(SelectionOption(value=r.asset_type, label=r.asset_type))
    if not options:
        return []
    return [SelectionGroup(label="Other_Asset", options=options)]


def get_stock_selection_groups(session: Session) -> list[SelectionGroup]:
    """Stock holdings grouped by asset_id (the parent stock account category).

    Each option's label is ``"<stock_code> <stock_name>"`` so the user can
    pick by ticker or by company name in a filterable dropdown.
    """
    rows = session.exec(
        select(StockJournal).order_by(
            StockJournal.asset_id.asc(), StockJournal.stock_id.asc()
        )
    ).all()
    if not rows:
        return []
    grouped: dict[str, list[StockJournal]] = {}
    for s in rows:
        grouped.setdefault(s.asset_id, []).append(s)
    return [
        SelectionGroup(
            label=key,
            options=[
                SelectionOption(value=s.stock_id, label=f"{s.stock_code} {s.stock_name}")
                for s in items
            ],
        )
        for key, items in grouped.items()
    ]


def get_stock_category_selection_groups(session: Session) -> list[SelectionGroup]:
    """Active stock categories as a single group labelled 'Stock_Category'.

    Drives the allocation-category dropdown on the stock holding form. Inactive
    (in_use != 'Y') categories are excluded so retired classes stop appearing
    for new holdings while existing holdings keep their reference.
    """
    rows = session.exec(
        select(StockCategory)
        .where(StockCategory.in_use == "Y")
        .order_by(StockCategory.category_index.asc(), StockCategory.category_id.asc())
    ).all()
    if not rows:
        return []
    return [
        SelectionGroup(
            label="Stock_Category",
            options=[
                SelectionOption(value=c.category_id, label=c.name) for c in rows
            ],
        )
    ]


def get_insurance_selection_groups(session: Session) -> list[SelectionGroup]:
    """Open insurance policies as a single group labelled 'Insurance'.

    Insurance uses `has_closed` (Y/N) instead of `in_use`; active = not closed.
    """
    rows = session.exec(
        select(Insurance)
        .where(Insurance.has_closed != "Y")
        .order_by(Insurance.insurance_id.asc())
    ).all()
    if not rows:
        return []
    return [
        SelectionGroup(
            label="Insurance",
            options=[
                SelectionOption(value=i.insurance_id, label=i.insurance_name)
                for i in rows
            ],
        )
    ]


def get_estate_selection_groups(session: Session) -> list[SelectionGroup]:
    """Active estates as a single group labelled 'Estate'.

    Excludes sold estates (estate_status == 'sold'); the option label is the
    estate's display name so the user can pick by property in a filterable
    dropdown.
    """
    rows = session.exec(
        select(Estate)
        .where(Estate.estate_status != "sold")
        .order_by(Estate.estate_id.asc())
    ).all()
    if not rows:
        return []
    return [
        SelectionGroup(
            label="Estate",
            options=[
                SelectionOption(value=e.estate_id, label=e.estate_name) for e in rows
            ],
        )
    ]


def get_code_selection_groups(session: Session) -> list[SelectionGroup]:
    """Top-level codes (parent_id IS NULL) consolidated into one group per code_type.

    Rows are queried ordered by code_index so options inside each group follow
    that order; group order is the first-seen code_type.
    """
    rows = session.exec(
        select(CodeData)
        .where(CodeData.in_use == "Y")
        .where(CodeData.parent_id.is_(None))
        .order_by(CodeData.code_index.asc(), CodeData.code_id.asc())
    ).all()
    grouped: dict[str, list[CodeData]] = {}
    for c in rows:
        grouped.setdefault(c.code_type, []).append(c)
    return [
        SelectionGroup(
            label=key,
            options=[SelectionOption(value=c.code_id, label=c.name) for c in items],
        )
        for key, items in grouped.items()
    ]


def get_sub_code_selection_groups(
    session: Session, parent_id: str
) -> list[SelectionGroup]:
    """Children of a parent code, returned as a single 'sub' group.

    Raises 404 when the parent has no children.
    """
    rows = session.exec(
        select(CodeData)
        .where(CodeData.parent_id == parent_id)
        .where(CodeData.in_use == "Y")
        .order_by(CodeData.code_index.asc(), CodeData.code_id.asc())
    ).all()
    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"No sub-codes for parent: {parent_id}",
        )
    return [
        SelectionGroup(
            label="sub",
            options=[SelectionOption(value=c.code_id, label=c.name) for c in rows],
        )
    ]
