"""Income statement (收支表) response schemas — Reports domain.

Per-period income / fixed / floating / net plus an annual summary with a
savings rate. Powers the top-of-page overview on the year-report/spending view.
Invest and transfer rows are excluded upstream: they are balance-sheet swaps,
not operating income or expense.
"""
from __future__ import annotations

from typing import Literal

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

_POINT_EXAMPLE = {
    "period": "202403",
    "income": 80000.0,
    "fixed": 25000.0,
    "floating": 18000.0,
    "expense": 43000.0,
    "net": 37000.0,
    "loan_repayment": 9200.0,
}


class IncomeExpensePoint(SQLModel):
    period: str = Field(
        ...,
        description="YYYYMM for monthly or YYYY for yearly",
        schema_extra={"examples": ["202403"]},
    )
    income: float = Field(
        ...,
        description="Income in base currency, positive",
        schema_extra={"examples": [80000.0]},
    )
    fixed: float = Field(
        ...,
        description="Fixed-expense magnitude, positive",
        schema_extra={"examples": [25000.0]},
    )
    floating: float = Field(
        ...,
        description="Variable-expense magnitude, positive",
        schema_extra={"examples": [18000.0]},
    )
    expense: float = Field(
        ...,
        description="Total expense = fixed + floating, positive",
        schema_extra={"examples": [43000.0]},
    )
    net: float = Field(
        ...,
        description="income - expense, signed (negative = overspent)",
        schema_extra={"examples": [37000.0]},
    )
    loan_repayment: float = Field(
        default=0.0,
        description=(
            "Loan repayment cash outflow (principal + interest, positive) from "
            "Loan_Journal. Purely additive context for the spending chart — NOT "
            "included in expense / net / savings_rate (those stay consumption-basis)."
        ),
        schema_extra={"examples": [9200.0]},
    )

    model_config = ConfigDict(json_schema_extra={"example": _POINT_EXAMPLE})


_SUMMARY_EXAMPLE = {
    "total_income": 960000.0,
    "total_expense": 516000.0,
    "net": 444000.0,
    "savings_rate": 0.4625,
}


class IncomeExpenseSummary(SQLModel):
    total_income: float = Field(
        ...,
        description="Sum of income across all periods in the window",
        schema_extra={"examples": [960000.0]},
    )
    total_expense: float = Field(
        ...,
        description="Sum of expense across all periods in the window",
        schema_extra={"examples": [516000.0]},
    )
    net: float = Field(
        ...,
        description="total_income - total_expense (net savings)",
        schema_extra={"examples": [444000.0]},
    )
    savings_rate: float = Field(
        ...,
        description="net / total_income; 0 when no income, may be negative",
        schema_extra={"examples": [0.4625]},
    )

    model_config = ConfigDict(json_schema_extra={"example": _SUMMARY_EXAMPLE})


class IncomeExpenseReportRead(SQLModel):
    type: Literal["monthly", "yearly"] = Field(
        ..., description="Aggregation granularity", schema_extra={"examples": ["monthly"]}
    )
    points: list[IncomeExpensePoint] = Field(
        ...,
        description="Time series, oldest first",
        schema_extra={"examples": [[_POINT_EXAMPLE]]},
    )
    summary: IncomeExpenseSummary = Field(
        ..., description="Totals and savings rate across the window"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "monthly",
                "points": [_POINT_EXAMPLE],
                "summary": _SUMMARY_EXAMPLE,
            }
        }
    )
