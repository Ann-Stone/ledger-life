"""Pure bookkeeping logic the guided flow accumulates into, kept free of any
Telegram types so it is unit-testable on its own.

A :class:`JournalDraft` is filled step by step (amount → direction → category →
payment source); :func:`record_draft` turns a complete draft into a
``JournalCreate`` and persists it via the existing ``create_journal`` service —
no settlement step, immediately visible in the ledger.

Category/payment options are derived from the same selection-group service the
frontend dropdowns use, so the bot always offers exactly the user's configured
accounts, cards, and codes.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

from sqlmodel import Session

from app.models.monthly_report.journal import Journal, JournalCreate
from app.services.journal_types import (
    EXPENSE_MAIN_TYPES,
    INCOME_MAIN_TYPES,
    norm_type,
)
from app.services.monthly_report_service import create_journal
from app.services.utility_service import (
    get_account_selection_groups,
    get_code_selection_groups,
    get_credit_card_selection_groups,
)

# Direction values used across the flow / draft.
EXPENSE = "expense"
INCOME = "income"

# First numeric token: optional sign, digits with optional thousands separators
# and an optional decimal part. Used to pull the amount out of a free-text line.
_NUMBER = re.compile(r"-?\d[\d,]*(?:\.\d+)?")


@dataclass
class JournalDraft:
    """Accumulating state for one bookkeeping entry (positive ``amount``)."""

    amount: float | None = None
    note: str | None = None
    direction: str | None = None  # EXPENSE | INCOME
    action_main: str | None = None
    action_main_type: str | None = None
    spend_way: str | None = None
    spend_way_type: str | None = None  # "account" | "credit_card"


@dataclass(frozen=True)
class CategoryOption:
    code_id: str  # -> action_main
    label: str
    code_type: str  # -> action_main_type (the selection group's label)


@dataclass(frozen=True)
class PaymentOption:
    value: str  # -> spend_way (Account.id or credit_card_id)
    label: str
    spend_way_type: str  # "account" | "credit_card"


def parse_amount_note(text: str) -> tuple[float, str | None] | None:
    """Parse a free-text line into ``(amount, note)``.

    The first number in the line is the amount (taken as a positive magnitude —
    the sign comes from the 支出/收入 choice, not the text); everything else is the
    note. Returns ``None`` when there is no usable non-zero number.
    """
    match = _NUMBER.search(text or "")
    if match is None:
        return None
    amount = abs(float(match.group(0).replace(",", "")))
    if amount == 0:
        return None
    note = (text[: match.start()] + text[match.end() :]).strip()
    return amount, (note or None)


def signed_spending(amount: float, direction: str) -> float:
    """Apply the ledger sign convention: income positive, expense negative."""
    magnitude = abs(amount)
    return magnitude if direction == INCOME else -magnitude


def category_options(session: Session, direction: str) -> list[CategoryOption]:
    """Top-level codes valid for ``direction``, flattened for button rendering.

    Filters the live selection groups by their type bucket: expense → fixed /
    floating, income → income / passive (the income bucket includes passive so
    dividends/interest/rent are loggable). Uses ``norm_type`` because production
    ``code_type`` casing is inconsistent.
    """
    allowed = EXPENSE_MAIN_TYPES if direction == EXPENSE else INCOME_MAIN_TYPES
    out: list[CategoryOption] = []
    for group in get_code_selection_groups(session):
        if norm_type(group.label) in allowed:
            out.extend(
                CategoryOption(opt.value, opt.label, group.label)
                for opt in group.options
            )
    return out


def payment_options(session: Session) -> list[PaymentOption]:
    """All active accounts then credit cards, each tagged with its spend_way type."""
    out: list[PaymentOption] = []
    for group in get_account_selection_groups(session):
        out.extend(
            PaymentOption(opt.value, opt.label, "account") for opt in group.options
        )
    for group in get_credit_card_selection_groups(session):
        out.extend(
            PaymentOption(opt.value, opt.label, "credit_card")
            for opt in group.options
        )
    return out


def draft_to_journal_create(draft: JournalDraft, *, today: date) -> JournalCreate:
    """Build a ``JournalCreate`` from a complete draft (raises if fields missing)."""
    required = (
        "amount",
        "direction",
        "action_main",
        "action_main_type",
        "spend_way",
        "spend_way_type",
    )
    missing = [name for name in required if getattr(draft, name) in (None, "")]
    if missing:
        raise ValueError(f"incomplete draft, missing: {', '.join(missing)}")

    spend_way_table = "Account" if draft.spend_way_type == "account" else "Credit_Card"
    return JournalCreate(
        vesting_month=today.strftime("%Y%m"),
        spend_date=today.strftime("%Y%m%d"),
        spend_way=draft.spend_way,
        spend_way_type=draft.spend_way_type,
        spend_way_table=spend_way_table,
        action_main=draft.action_main,
        action_main_type=draft.action_main_type,
        action_main_table="Code_Data",
        action_sub=None,
        action_sub_type=None,
        action_sub_table=None,
        spending=signed_spending(draft.amount, draft.direction),
        invoice_number=None,
        note=draft.note,
    )


def record_draft(
    session: Session, draft: JournalDraft, *, today: date | None = None
) -> Journal:
    """Persist a complete draft as a Journal entry and return the saved row."""
    if today is None:
        today = date.today()
    return create_journal(session, draft_to_journal_create(draft, today=today))
