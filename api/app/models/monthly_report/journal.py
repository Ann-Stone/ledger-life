"""Journal (transaction) model and CRUD schemas (Monthly Report domain).

Polymorphic reference fields
----------------------------
Journal carries two polymorphic references that the frontend must resolve to
form labels and validate before submit. The valid combinations are:

``spend_way`` (payment source) — always the primary key of the source row:
  - ``spend_way_type="account"`` + ``spend_way_table="Account"``
    → ``spend_way`` is an ``Account.id`` (stringified PK, e.g. ``"1"``)
  - ``spend_way_type="credit_card"`` + ``spend_way_table="Credit_Card"``
    → ``spend_way`` is a ``CreditCard.credit_card_id`` (its PK, e.g. ``CC-VISA-01``)

``action_main`` / ``action_sub`` (classification codes)
  - ``action_main_type`` is the ``Code_Data.code_type`` of the referenced row
    (typical values: ``Fixed``, ``Floating``, ``Income``, ``Invest``,
    ``Transfer``); the literal set is user-configurable in the Settings →
    Codes table.
  - ``action_main_table`` is always ``"Code_Data"`` for code-driven entries.
  - ``action_sub`` mirrors ``action_main`` and references a sub-code (a
    ``Code_Data`` row whose ``parent_id`` equals ``action_main``). Either all
    three ``action_sub_*`` fields are non-null together, or all three are null.

The ``api/docs/api-reference.md`` exporter renders a machine-readable
constraint matrix from this docstring; do not move the references without
updating ``app/scripts/export_docs.py``.
"""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


_SPEND_WAY_TYPE_DESC = (
    "Polymorphic discriminator for spend_way. Valid values: 'account' "
    "(spend_way_table='Account', spend_way → Account.id PK) | "
    "'credit_card' (spend_way_table='Credit_Card', spend_way → "
    "CreditCard.credit_card_id PK)."
)
_SPEND_WAY_TABLE_DESC = (
    "Source SQL table for spend_way. Must be 'Account' when "
    "spend_way_type='account', or 'Credit_Card' when "
    "spend_way_type='credit_card'."
)
_ACTION_MAIN_DESC = (
    "Reference to a Code_Data row's code_id. The set of valid code_ids is "
    "user-configurable via Settings → Codes."
)
_ACTION_MAIN_TYPE_DESC = (
    "Mirror of the referenced Code_Data.code_type. Common values: 'Fixed', "
    "'Floating', 'Income', 'Invest', 'Transfer'. Frontend should fetch "
    "/utilities/selections/codes for the live set."
)
_ACTION_MAIN_TABLE_DESC = (
    "Source SQL table for action_main. Always 'Code_Data' for code-driven "
    "classification."
)
_ACTION_SUB_DESC = (
    "Optional sub-classification: a Code_Data.code_id whose parent_id equals "
    "action_main. Null when there is no secondary breakdown."
)
_ACTION_SUB_TYPE_DESC = (
    "Mirror of the sub-code's Code_Data.code_type. Null when action_sub is "
    "null. Either all three action_sub_* fields are populated together or "
    "all three are null."
)
_ACTION_SUB_TABLE_DESC = (
    "Source SQL table for action_sub. 'Code_Data' when action_sub is set, "
    "null otherwise."
)


_JOURNAL_EXAMPLE = {
    "distinct_number": 1,
    "vesting_month": "202604",
    "spend_date": "20260418",
    "spend_way": "1",
    "spend_way_type": "account",
    "spend_way_table": "Account",
    "action_main": "EXP01",
    "action_main_type": "expense",
    "action_main_table": "Code_Data",
    "action_sub": None,
    "action_sub_type": None,
    "action_sub_table": None,
    "spending": -123.45,
    "invoice_number": None,
    "note": "Lunch",
}


class Journal(SQLModel, table=True):
    __tablename__ = "Journal"

    distinct_number: int | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"autoincrement": True},
        description="Autoincrement PK",
        schema_extra={"examples": [1]},
    )
    vesting_month: str = Field(..., description="YYYYMM", schema_extra={"examples": ["202604"]})
    spend_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20260418"]})
    spend_way: str = Field(..., description="Account or credit card id used for payment", schema_extra={"examples": ["1"]})
    spend_way_type: str = Field(..., description=_SPEND_WAY_TYPE_DESC, schema_extra={"examples": ["account"]})
    spend_way_table: str = Field(..., description=_SPEND_WAY_TABLE_DESC, schema_extra={"examples": ["Account"]})
    action_main: str = Field(..., description=_ACTION_MAIN_DESC, schema_extra={"examples": ["EXP01"]})
    action_main_type: str = Field(..., description=_ACTION_MAIN_TYPE_DESC, schema_extra={"examples": ["expense"]})
    action_main_table: str = Field(..., description=_ACTION_MAIN_TABLE_DESC, schema_extra={"examples": ["Code_Data"]})
    action_sub: str | None = Field(default=None, description=_ACTION_SUB_DESC, schema_extra={"examples": [None]})
    action_sub_type: str | None = Field(default=None, description=_ACTION_SUB_TYPE_DESC, schema_extra={"examples": [None]})
    action_sub_table: str | None = Field(default=None, description=_ACTION_SUB_TABLE_DESC, schema_extra={"examples": [None]})
    spending: float = Field(..., description="Positive = income, negative = expense", schema_extra={"examples": [-123.45]})
    invoice_number: str | None = Field(default=None, description="Invoice number, populated by invoice CSV import", schema_extra={"examples": ["AB12345678"]})
    note: str | None = Field(default=None, description="Free-form note", schema_extra={"examples": ["Lunch"]})

    model_config = ConfigDict(json_schema_extra={"example": _JOURNAL_EXAMPLE})


class JournalCreate(SQLModel):
    vesting_month: str = Field(..., description="YYYYMM", schema_extra={"examples": ["202604"]})
    spend_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20260418"]})
    spend_way: str = Field(..., description="Payment source id", schema_extra={"examples": ["1"]})
    spend_way_type: str = Field(..., description=_SPEND_WAY_TYPE_DESC, schema_extra={"examples": ["account"]})
    spend_way_table: str = Field(..., description=_SPEND_WAY_TABLE_DESC, schema_extra={"examples": ["Account"]})
    action_main: str = Field(..., description=_ACTION_MAIN_DESC, schema_extra={"examples": ["EXP01"]})
    action_main_type: str = Field(..., description=_ACTION_MAIN_TYPE_DESC, schema_extra={"examples": ["expense"]})
    action_main_table: str = Field(..., description=_ACTION_MAIN_TABLE_DESC, schema_extra={"examples": ["Code_Data"]})
    action_sub: str | None = Field(default=None, description=_ACTION_SUB_DESC, schema_extra={"examples": [None]})
    action_sub_type: str | None = Field(default=None, description=_ACTION_SUB_TYPE_DESC, schema_extra={"examples": [None]})
    action_sub_table: str | None = Field(default=None, description=_ACTION_SUB_TABLE_DESC, schema_extra={"examples": [None]})
    spending: float = Field(..., description="Positive = income, negative = expense", schema_extra={"examples": [-123.45]})
    invoice_number: str | None = Field(default=None, description="Invoice number", schema_extra={"examples": ["AB12345678"]})
    note: str | None = Field(default=None, description="Free-form note", schema_extra={"examples": ["Lunch"]})

    model_config = ConfigDict(
        json_schema_extra={"example": {k: v for k, v in _JOURNAL_EXAMPLE.items() if k != "distinct_number"}}
    )


class JournalUpdate(SQLModel):
    vesting_month: str | None = Field(default=None, description="YYYYMM", schema_extra={"examples": ["202604"]})
    spend_date: str | None = Field(default=None, description="YYYYMMDD", schema_extra={"examples": ["20260418"]})
    spend_way: str | None = Field(default=None, description="Payment source id", schema_extra={"examples": ["1"]})
    spend_way_type: str | None = Field(default=None, description=_SPEND_WAY_TYPE_DESC, schema_extra={"examples": ["account"]})
    spend_way_table: str | None = Field(default=None, description=_SPEND_WAY_TABLE_DESC, schema_extra={"examples": ["Account"]})
    action_main: str | None = Field(default=None, description=_ACTION_MAIN_DESC, schema_extra={"examples": ["EXP01"]})
    action_main_type: str | None = Field(default=None, description=_ACTION_MAIN_TYPE_DESC, schema_extra={"examples": ["expense"]})
    action_main_table: str | None = Field(default=None, description=_ACTION_MAIN_TABLE_DESC, schema_extra={"examples": ["Code_Data"]})
    action_sub: str | None = Field(default=None, description=_ACTION_SUB_DESC, schema_extra={"examples": [None]})
    action_sub_type: str | None = Field(default=None, description=_ACTION_SUB_TYPE_DESC, schema_extra={"examples": [None]})
    action_sub_table: str | None = Field(default=None, description=_ACTION_SUB_TABLE_DESC, schema_extra={"examples": [None]})
    spending: float | None = Field(default=None, description="Signed amount", schema_extra={"examples": [-123.45]})
    invoice_number: str | None = Field(default=None, description="Invoice number", schema_extra={"examples": ["AB12345678"]})
    note: str | None = Field(default=None, description="Free-form note", schema_extra={"examples": ["Updated"]})

    model_config = ConfigDict(json_schema_extra={"example": {"note": "Updated note"}})


class JournalMonthRead(SQLModel):
    items: list["JournalRead"] = Field(
        ...,
        description="Journal entries for the month, ordered by spend_date",
        schema_extra={"examples": [[_JOURNAL_EXAMPLE]]},
    )
    gain_loss: float = Field(
        ...,
        description="Net gain/loss for the month after FX conversion to base currency",
        schema_extra={"examples": [1234.56]},
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"items": [_JOURNAL_EXAMPLE], "gain_loss": 1234.56}}
    )


class JournalRead(SQLModel):
    distinct_number: int = Field(..., description="Autoincrement PK", schema_extra={"examples": [1]})
    vesting_month: str = Field(..., description="YYYYMM", schema_extra={"examples": ["202604"]})
    spend_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20260418"]})
    spend_way: str = Field(..., description="Payment source id", schema_extra={"examples": ["1"]})
    spend_way_type: str = Field(..., description=_SPEND_WAY_TYPE_DESC, schema_extra={"examples": ["account"]})
    spend_way_table: str = Field(..., description=_SPEND_WAY_TABLE_DESC, schema_extra={"examples": ["Account"]})
    action_main: str = Field(..., description=_ACTION_MAIN_DESC, schema_extra={"examples": ["EXP01"]})
    action_main_type: str = Field(..., description=_ACTION_MAIN_TYPE_DESC, schema_extra={"examples": ["expense"]})
    action_main_table: str = Field(..., description=_ACTION_MAIN_TABLE_DESC, schema_extra={"examples": ["Code_Data"]})
    action_sub: str | None = Field(default=None, description=_ACTION_SUB_DESC, schema_extra={"examples": [None]})
    action_sub_type: str | None = Field(default=None, description=_ACTION_SUB_TYPE_DESC, schema_extra={"examples": [None]})
    action_sub_table: str | None = Field(default=None, description=_ACTION_SUB_TABLE_DESC, schema_extra={"examples": [None]})
    spending: float = Field(..., description="Signed amount", schema_extra={"examples": [-123.45]})
    invoice_number: str | None = Field(default=None, description="Invoice number", schema_extra={"examples": ["AB12345678"]})
    note: str | None = Field(default=None, description="Free-form note", schema_extra={"examples": ["Lunch"]})

    model_config = ConfigDict(json_schema_extra={"example": _JOURNAL_EXAMPLE})


JournalMonthRead.model_rebuild()
