"""Composite payloads that write a Journal row together with an asset detail row.

Used by ``POST /monthly-report/journals/stock-transaction`` to record a single
real-world event (e.g. "bought 10 shares of AAPL") as one atomic transaction
spanning the ``Journal`` and ``Stock_Detail`` tables.

The two writes succeed or fail together; on any error the surrounding session
is rolled back by FastAPI's dependency teardown.
"""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

from app.models.assets.estate import EstateExcuteType, EstateJournalRead
from app.models.assets.insurance import InsuranceExcuteType, InsuranceJournalRead
from app.models.assets.loan import LoanJournalRead
from app.models.assets.stock import StockDetailRead, StockExcuteType
from app.models.monthly_report.journal import JournalCreate, JournalRead, JournalUpdate


_STOCK_TRANSACTION_DETAIL_EXAMPLE = {
    "stock_id": "STK-H-001",
    "excute_type": "buy",
    "excute_amount": 10.0,
    "excute_date": "20260418",
    "memo": "First lot",
}


class StockTransactionDetailCreate(SQLModel):
    """Stock_Detail subset accepted by the composite endpoint.

    ``excute_price`` is intentionally absent: the service copies
    ``journal.spending`` into it verbatim (sign preserved — a buy/outflow
    journal is negative, so the detail's price is negative too).
    ``account_id``/``account_name`` are also absent: they are resolved from
    ``journal.spend_way`` by the service so the two rows stay in sync.

    ``excute_amount`` defaults to 0.0 so cash dividends (no share count)
    can omit it; stock splits / stock dividends can keep amount and rely on
    ``journal.spending`` being 0 to imply ``excute_price = 0``.
    """

    stock_id: str = Field(
        ...,
        description="Existing StockJournal.stock_id this transaction belongs to.",
        schema_extra={"examples": ["STK-H-001"]},
    )
    excute_type: StockExcuteType = Field(
        ...,
        description="buy / sell / stock (split or stock dividend) / cash (cash dividend)",
        schema_extra={"examples": ["buy"]},
    )
    excute_amount: float = Field(
        default=0.0,
        description=(
            "Quantity traded (shares). Defaults to 0 so cash dividends "
            "(excute_type='cash') can omit it."
        ),
        schema_extra={"examples": [10.0]},
    )
    excute_date: str | None = Field(
        default=None,
        description="YYYYMMDD; defaults to journal.spend_date when omitted.",
        schema_extra={"examples": ["20260418"]},
    )
    memo: str | None = Field(
        default=None,
        description="Free-form memo; defaults to journal.note when omitted.",
        schema_extra={"examples": ["First lot"]},
    )

    model_config = ConfigDict(
        json_schema_extra={"example": _STOCK_TRANSACTION_DETAIL_EXAMPLE}
    )


class JournalStockTransactionCreate(SQLModel):
    """Composite payload: Journal + Stock_Detail written atomically."""

    journal: JournalCreate = Field(..., description="Journal row to insert.")
    stock_detail: StockTransactionDetailCreate = Field(
        ..., description="Stock detail row derived from + linked to the journal."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "journal": {
                    "vesting_month": "202604",
                    "spend_date": "20260418",
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
                },
                "stock_detail": _STOCK_TRANSACTION_DETAIL_EXAMPLE,
            }
        }
    )


class JournalStockTransactionUpdate(SQLModel):
    """Composite payload for editing a Journal while creating its first Stock_Detail.

    Used when a user edits a previously-untagged journal and now classifies it
    as a stock transaction (e.g. correcting an imported bank entry). The Journal
    is updated in place; the Stock_Detail is always created fresh — partial
    edits of existing details belong on the independent Stock_Detail endpoints.
    """

    journal: JournalUpdate = Field(..., description="Journal fields to update.")
    stock_detail: StockTransactionDetailCreate = Field(
        ..., description="Stock detail row to insert alongside the update."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "journal": {
                    "action_main": "TRA",
                    "action_main_type": "Transfer",
                    "action_main_table": "Code_Data",
                    "action_sub": "Stock",
                    "action_sub_type": "Asset",
                    "action_sub_table": "Stock_Detail",
                    "note": "Re-classified as stock purchase",
                },
                "stock_detail": _STOCK_TRANSACTION_DETAIL_EXAMPLE,
            }
        }
    )


class JournalStockTransactionRead(SQLModel):
    """Response body for the composite endpoint."""

    journal: JournalRead = Field(..., description="Persisted journal row.")
    stock_detail: StockDetailRead = Field(..., description="Persisted stock detail row.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "journal": {
                    "distinct_number": 42,
                    "vesting_month": "202604",
                    "spend_date": "20260418",
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
                },
                "stock_detail": {
                    "distinct_number": 17,
                    "stock_id": "STK-H-001",
                    "excute_type": "buy",
                    "excute_amount": 10.0,
                    "excute_price": -1805.0,
                    "excute_date": "20260418",
                    "account_id": "BANK-CHASE-01",
                    "account_name": "Chase Checking",
                    "memo": "First lot",
                },
            }
        }
    )


# --------------------------------------------------------------------------- #
# Insurance composite payloads
#
# Mirrors the Stock variants above. Two divergences, both driven by the
# Insurance_Journal schema:
#   * Insurance_Journal has no account columns, so there is nothing to resolve
#     from ``journal.spend_way`` — settling-source fields are simply absent.
#   * ``excute_price`` (the amount) is the signed pass-through field: it is
#     copied verbatim from ``journal.spending`` (premium/outflow stays negative,
#     refund/inflow stays positive), so the payload omits it.
# --------------------------------------------------------------------------- #


_INSURANCE_TRANSACTION_DETAIL_EXAMPLE = {
    "insurance_id": "INS-001",
    "insurance_excute_type": "pay",
    "excute_date": "20260115",
    "memo": "Annual premium",
}


class InsuranceTransactionDetailCreate(SQLModel):
    """Insurance_Journal subset accepted by the composite endpoint.

    ``excute_price`` is intentionally absent: the service copies
    ``journal.spending`` into it verbatim (sign preserved — a premium/outflow
    journal is negative, a refund/inflow is positive). There are no
    account fields to resolve: Insurance_Journal stores only the policy link,
    type, amount, date and memo.
    """

    insurance_id: str = Field(
        ...,
        description="Existing Insurance.insurance_id this transaction belongs to.",
        schema_extra={"examples": ["INS-001"]},
    )
    insurance_excute_type: InsuranceExcuteType = Field(
        ...,
        description="pay / cash / return / expect",
        schema_extra={"examples": ["pay"]},
    )
    excute_date: str | None = Field(
        default=None,
        description="YYYYMMDD; defaults to journal.spend_date when omitted.",
        schema_extra={"examples": ["20260115"]},
    )
    memo: str | None = Field(
        default=None,
        description="Free-form memo; defaults to journal.note when omitted.",
        schema_extra={"examples": ["Annual premium"]},
    )

    model_config = ConfigDict(
        json_schema_extra={"example": _INSURANCE_TRANSACTION_DETAIL_EXAMPLE}
    )


class JournalInsuranceTransactionCreate(SQLModel):
    """Composite payload: Journal + Insurance_Journal written atomically."""

    journal: JournalCreate = Field(..., description="Journal row to insert.")
    insurance_detail: InsuranceTransactionDetailCreate = Field(
        ..., description="Insurance detail row derived from + linked to the journal."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "journal": {
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
                },
                "insurance_detail": _INSURANCE_TRANSACTION_DETAIL_EXAMPLE,
            }
        }
    )


class JournalInsuranceTransactionUpdate(SQLModel):
    """Composite payload for editing a Journal while creating its first Insurance_Journal.

    Used when a user edits a previously-untagged journal and now classifies it
    as an insurance transaction. The Journal is updated in place; the
    Insurance_Journal is always created fresh — partial edits of existing
    details belong on the independent Insurance_Journal endpoints.
    """

    journal: JournalUpdate = Field(..., description="Journal fields to update.")
    insurance_detail: InsuranceTransactionDetailCreate = Field(
        ..., description="Insurance detail row to insert alongside the update."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "journal": {
                    "action_main": "TRA",
                    "action_main_type": "Transfer",
                    "action_main_table": "Code_Data",
                    "action_sub": "Insurance",
                    "action_sub_type": "Asset",
                    "action_sub_table": "Insurance_Journal",
                    "note": "Re-classified as premium payment",
                },
                "insurance_detail": _INSURANCE_TRANSACTION_DETAIL_EXAMPLE,
            }
        }
    )


class JournalInsuranceTransactionRead(SQLModel):
    """Response body for the insurance composite endpoint."""

    journal: JournalRead = Field(..., description="Persisted journal row.")
    insurance_detail: InsuranceJournalRead = Field(
        ..., description="Persisted insurance detail row."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "journal": {
                    "distinct_number": 42,
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
                },
                "insurance_detail": {
                    "distinct_number": 17,
                    "insurance_id": "INS-001",
                    "insurance_excute_type": "pay",
                    "excute_price": -1200.0,
                    "excute_date": "20260115",
                    "memo": "Annual premium",
                },
            }
        }
    )


# --------------------------------------------------------------------------- #
# Estate composite payloads
#
# Same shape and divergences as the Insurance variants: no account columns on
# Estate_Journal, and ``excute_price`` is the signed pass-through field.
# --------------------------------------------------------------------------- #


_ESTATE_TRANSACTION_DETAIL_EXAMPLE = {
    "estate_id": "EST-001",
    "estate_excute_type": "tax",
    "excute_date": "20260115",
    "memo": "Property tax",
}


class EstateTransactionDetailCreate(SQLModel):
    """Estate_Journal subset accepted by the composite endpoint.

    ``excute_price`` is intentionally absent: the service copies
    ``journal.spending`` into it verbatim (sign preserved — a tax/fee/outflow
    journal is negative, a rent/inflow is positive). There are no account
    fields to resolve: Estate_Journal stores only the estate link, type,
    amount, date and memo.
    """

    estate_id: str = Field(
        ...,
        description="Existing Estate.estate_id this transaction belongs to.",
        schema_extra={"examples": ["EST-001"]},
    )
    estate_excute_type: EstateExcuteType = Field(
        ...,
        description="tax / fee / insurance / fix / rent / deposit",
        schema_extra={"examples": ["tax"]},
    )
    excute_date: str | None = Field(
        default=None,
        description="YYYYMMDD; defaults to journal.spend_date when omitted.",
        schema_extra={"examples": ["20260115"]},
    )
    memo: str | None = Field(
        default=None,
        description="Free-form memo; defaults to journal.note when omitted.",
        schema_extra={"examples": ["Property tax"]},
    )

    model_config = ConfigDict(
        json_schema_extra={"example": _ESTATE_TRANSACTION_DETAIL_EXAMPLE}
    )


class JournalEstateTransactionCreate(SQLModel):
    """Composite payload: Journal + Estate_Journal written atomically."""

    journal: JournalCreate = Field(..., description="Journal row to insert.")
    estate_detail: EstateTransactionDetailCreate = Field(
        ..., description="Estate detail row derived from + linked to the journal."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "journal": {
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
                },
                "estate_detail": _ESTATE_TRANSACTION_DETAIL_EXAMPLE,
            }
        }
    )


class JournalEstateTransactionUpdate(SQLModel):
    """Composite payload for editing a Journal while creating its first Estate_Journal.

    Used when a user edits a previously-untagged journal and now classifies it
    as an estate transaction. The Journal is updated in place; the
    Estate_Journal is always created fresh — partial edits of existing details
    belong on the independent Estate_Journal endpoints.
    """

    journal: JournalUpdate = Field(..., description="Journal fields to update.")
    estate_detail: EstateTransactionDetailCreate = Field(
        ..., description="Estate detail row to insert alongside the update."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "journal": {
                    "action_main": "TRA",
                    "action_main_type": "Transfer",
                    "action_main_table": "Code_Data",
                    "action_sub": "Estate",
                    "action_sub_type": "Asset",
                    "action_sub_table": "Estate_Journal",
                    "note": "Re-classified as property tax",
                },
                "estate_detail": _ESTATE_TRANSACTION_DETAIL_EXAMPLE,
            }
        }
    )


class JournalEstateTransactionRead(SQLModel):
    """Response body for the estate composite endpoint."""

    journal: JournalRead = Field(..., description="Persisted journal row.")
    estate_detail: EstateJournalRead = Field(
        ..., description="Persisted estate detail row."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "journal": {
                    "distinct_number": 42,
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
                },
                "estate_detail": {
                    "distinct_number": 17,
                    "estate_id": "EST-001",
                    "estate_excute_type": "tax",
                    "excute_price": -8000.0,
                    "excute_date": "20260115",
                    "memo": "Property tax",
                },
            }
        }
    )


# --------------------------------------------------------------------------- #
# Loan composite payloads
#
# The biggest divergence from the other three composites: a single repayment is
# split into a principal portion and an interest portion, each written as a
# SEPARATE Loan_Journal row holding a POSITIVE magnitude — *not* a signed copy of
# journal.spending. That positive convention is what every loan reader expects:
# settlement (``balance = amount − Σprincipal``, ``repayed = Σprincipal``), the
# cash flow (interest→operating, principal→financing) and the income statement.
# The journal's signed ``spending`` is the total outflow ``−(principal+interest)``;
# the service validates the two agree. Loan_Journal has no account columns, so —
# like Insurance/Estate — there is no settling-source lookup.
# --------------------------------------------------------------------------- #


_LOAN_TRANSACTION_DETAIL_EXAMPLE = {
    "loan_id": "LN-001",
    "principal": 8000.0,
    "interest": 1200.0,
    "excute_date": "20260401",
    "memo": "April payment",
}


class LoanTransactionDetailCreate(SQLModel):
    """Loan repayment split accepted by the composite endpoint.

    ``principal`` and ``interest`` are POSITIVE magnitudes; the service stores
    each (when > 0) as its own ``Loan_Journal`` row and copies the values
    verbatim (no sign flip). Either portion may be 0 (an interest-only or
    principal-only payment) but not both. The journal ``spending`` is the signed
    total outflow ``−(principal+interest)``; the service rejects a mismatch.
    """

    loan_id: str = Field(
        ...,
        description="Existing Loan.loan_id this repayment belongs to.",
        schema_extra={"examples": ["LN-001"]},
    )
    principal: float = Field(
        default=0.0,
        ge=0,
        description="Principal portion (positive magnitude; reduces the loan balance).",
        schema_extra={"examples": [8000.0]},
    )
    interest: float = Field(
        default=0.0,
        ge=0,
        description="Interest portion (positive magnitude; an operating cost / expense).",
        schema_extra={"examples": [1200.0]},
    )
    excute_date: str | None = Field(
        default=None,
        description="YYYYMMDD; defaults to journal.spend_date when omitted.",
        schema_extra={"examples": ["20260401"]},
    )
    memo: str | None = Field(
        default=None,
        description="Free-form memo; defaults to journal.note when omitted.",
        schema_extra={"examples": ["April payment"]},
    )

    model_config = ConfigDict(
        json_schema_extra={"example": _LOAN_TRANSACTION_DETAIL_EXAMPLE}
    )


_LOAN_TRANSACTION_JOURNAL_EXAMPLE = {
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
    "note": "April mortgage payment",
}


class JournalLoanTransactionCreate(SQLModel):
    """Composite payload: Journal + one-or-two Loan_Journal rows written atomically."""

    journal: JournalCreate = Field(..., description="Journal row to insert.")
    loan_detail: LoanTransactionDetailCreate = Field(
        ..., description="Loan repayment split derived from + linked to the journal."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "journal": _LOAN_TRANSACTION_JOURNAL_EXAMPLE,
                "loan_detail": _LOAN_TRANSACTION_DETAIL_EXAMPLE,
            }
        }
    )


class JournalLoanTransactionUpdate(SQLModel):
    """Composite payload for editing a Journal while creating its Loan_Journal rows.

    Used when re-classifying a previously-untagged journal as a loan repayment.
    The Journal is updated in place; the Loan_Journal rows are always created
    fresh — partial edits of existing rows go through the independent
    Loan_Journal endpoints. Both writes succeed or both roll back.
    """

    journal: JournalUpdate = Field(..., description="Journal fields to update.")
    loan_detail: LoanTransactionDetailCreate = Field(
        ..., description="Loan repayment split to insert alongside the update."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "journal": {
                    "action_main": "LoanRepayment",
                    "action_main_type": "LoanRepayment",
                    "action_main_table": "Loan",
                    "action_sub": "LN-001",
                    "action_sub_type": "Loan",
                    "action_sub_table": "Loan",
                    "note": "Re-classified as loan repayment",
                },
                "loan_detail": _LOAN_TRANSACTION_DETAIL_EXAMPLE,
            }
        }
    )


class JournalLoanTransactionRead(SQLModel):
    """Response body for the loan composite endpoint (one or two detail rows)."""

    journal: JournalRead = Field(..., description="Persisted journal row.")
    loan_details: list[LoanJournalRead] = Field(
        ..., description="Persisted Loan_Journal rows (principal and/or interest)."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "journal": {"distinct_number": 42, **_LOAN_TRANSACTION_JOURNAL_EXAMPLE},
                "loan_details": [
                    {
                        "distinct_number": 17,
                        "loan_id": "LN-001",
                        "loan_excute_type": "principal",
                        "excute_price": 8000.0,
                        "excute_date": "20260401",
                        "memo": "April payment",
                    },
                    {
                        "distinct_number": 18,
                        "loan_id": "LN-001",
                        "loan_excute_type": "interest",
                        "excute_price": 1200.0,
                        "excute_date": "20260401",
                        "memo": "April payment",
                    },
                ],
            }
        }
    )
