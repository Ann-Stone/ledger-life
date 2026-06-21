"""Analytics response schemas for the Monthly Report domain.

These are read-only DTOs (not table models). Each schema has full Pydantic
documentation: every field uses ``Field(..., description=..., examples=[...])``
and every class carries a ``model_config`` with a full-model example.
"""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


# ---------- Expenditure ratio ----------

_RATIO_ITEM_EXAMPLE = {"name": "expense", "value": 1234.56}


class ExpenditureRatioItem(SQLModel):
    name: str = Field(
        ..., description="Category label", schema_extra={"examples": ["expense"]}
    )
    value: float = Field(
        ..., description="Aggregated absolute amount", schema_extra={"examples": [1234.56]}
    )

    model_config = ConfigDict(json_schema_extra={"example": _RATIO_ITEM_EXAMPLE})


class ExpenditureRatioResponse(SQLModel):
    outer: list[ExpenditureRatioItem] = Field(
        ...,
        description="Outer pie: amounts grouped by action_main_type",
        schema_extra={"examples": [[_RATIO_ITEM_EXAMPLE]]},
    )
    inner: list[ExpenditureRatioItem] = Field(
        ...,
        description="Inner pie: amounts grouped by action_sub_type",
        schema_extra={"examples": [[_RATIO_ITEM_EXAMPLE]]},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"outer": [_RATIO_ITEM_EXAMPLE], "inner": [_RATIO_ITEM_EXAMPLE]}
        }
    )


# ---------- Invest ratio ----------

_INVEST_ITEM_EXAMPLE = {"name": "stock", "value": 5000.0}


class InvestRatioItem(SQLModel):
    name: str = Field(
        ..., description="Invest sub-category label", schema_extra={"examples": ["stock"]}
    )
    value: float = Field(
        ..., description="Aggregated invest amount", schema_extra={"examples": [5000.0]}
    )

    model_config = ConfigDict(json_schema_extra={"example": _INVEST_ITEM_EXAMPLE})


class InvestRatioResponse(SQLModel):
    items: list[InvestRatioItem] = Field(
        ...,
        description="Per-subtype invest amounts",
        schema_extra={"examples": [[_INVEST_ITEM_EXAMPLE]]},
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"items": [_INVEST_ITEM_EXAMPLE]}}
    )


# ---------- Expenditure vs budget ----------

_BUDGET_ROW_EXAMPLE = {
    "action_main_type": "expense",
    "expected": 30000.0,
    "actual": 28500.5,
    "diff": -1499.5,
    "usage_rate": 0.95,
}


class ExpenditureBudgetRow(SQLModel):
    action_main_type: str = Field(
        ..., description="Action main type", schema_extra={"examples": ["expense"]}
    )
    expected: float = Field(
        ..., description="Expected amount from Budget", schema_extra={"examples": [30000.0]}
    )
    actual: float = Field(
        ..., description="Actual journal sum", schema_extra={"examples": [28500.5]}
    )
    diff: float = Field(
        ..., description="actual - expected", schema_extra={"examples": [-1499.5]}
    )
    usage_rate: float = Field(
        ..., description="actual / expected (0 when expected == 0)", schema_extra={"examples": [0.95]}
    )

    model_config = ConfigDict(json_schema_extra={"example": _BUDGET_ROW_EXAMPLE})


class ExpenditureBudgetResponse(SQLModel):
    rows: list[ExpenditureBudgetRow] = Field(
        ...,
        description="Per action_main_type comparison rows",
        schema_extra={"examples": [[_BUDGET_ROW_EXAMPLE]]},
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"rows": [_BUDGET_ROW_EXAMPLE]}}
    )


# ---------- Liability ----------

_LIABILITY_ITEM_EXAMPLE = {
    "credit_card_id": "CC-VISA-01",
    "credit_card_name": "Chase Sapphire",
    "amount": 2500.0,
}


class LiabilityItem(SQLModel):
    credit_card_id: str = Field(
        ...,
        description="Credit card business ID",
        schema_extra={"examples": ["CC-VISA-01"]},
    )
    credit_card_name: str = Field(
        ..., description="Credit card display name", schema_extra={"examples": ["Chase Sapphire"]}
    )
    amount: float = Field(
        ..., description="Aggregated charge amount for the month", schema_extra={"examples": [2500.0]}
    )

    model_config = ConfigDict(json_schema_extra={"example": _LIABILITY_ITEM_EXAMPLE})


class LiabilityResponse(SQLModel):
    items: list[LiabilityItem] = Field(
        ...,
        description="Per-card credit card liability for the month",
        schema_extra={"examples": [[_LIABILITY_ITEM_EXAMPLE]]},
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"items": [_LIABILITY_ITEM_EXAMPLE]}}
    )


# ---------- Uncategorized journals ----------

_UNCATEGORIZED_MONTH_EXAMPLE = {"vesting_month": "202405", "count": 87}


class UncategorizedMonthCount(SQLModel):
    vesting_month: str = Field(
        ..., description="YYYYMM the uncategorized rows belong to", schema_extra={"examples": ["202405"]}
    )
    count: int = Field(
        ..., description="Uncategorized journal rows in the month", schema_extra={"examples": [87]}
    )

    model_config = ConfigDict(json_schema_extra={"example": _UNCATEGORIZED_MONTH_EXAMPLE})


class UncategorizedSummaryResponse(SQLModel):
    total: int = Field(
        ...,
        description="Uncategorized journal rows across all months (action_main_type outside every report bucket)",
        schema_extra={"examples": [2330]},
    )
    months: list[UncategorizedMonthCount] = Field(
        ...,
        description="Per-month breakdown, newest month first; months with zero rows omitted",
        schema_extra={"examples": [[_UNCATEGORIZED_MONTH_EXAMPLE]]},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"total": 2330, "months": [_UNCATEGORIZED_MONTH_EXAMPLE]}
        }
    )
