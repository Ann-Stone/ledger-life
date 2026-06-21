"""Comprehensive income statement (綜合損益表) response schemas — Reports domain.

A true period profit-and-loss split into three sections, unlike the cash-flow
statement (which mixes in balance-sheet swaps: investing/financing principal):

* **本業損益 (operating)** — active income (``income`` type only, *not* passive)
  minus living expenses (fixed + floating).
* **投資損益 (investment)** — dividends/yield (``passive``), realized capital
  gains (booked ``資本利得`` journals), and the period change in unrealized
  market value (Δ of ``price − cost`` from StockNetValueHistory).
* **綜合損益 (comprehensive)** — operating_net + investment_net.

All amounts are FX-converted to the base currency. Income/expense magnitudes are
positive; the ``*_net`` and capital-gain fields are signed (negative = loss).
"""
from __future__ import annotations

from typing import Literal

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

_POINT_EXAMPLE = {
    "period": "202403",
    "active_income": 80000.0,
    "fixed": 25000.0,
    "floating": 18000.0,
    "loan_interest": 0.0,
    "operating_net": 37000.0,
    "dividend": 3000.0,
    "realized": 5000.0,
    "unrealized": 12000.0,
    "investment_net": 20000.0,
    "comprehensive_net": 57000.0,
}


class IncomeStatementPoint(SQLModel):
    period: str = Field(
        ...,
        description="YYYYMM for monthly or YYYY for yearly",
        schema_extra={"examples": ["202403"]},
    )
    active_income: float = Field(
        ...,
        description="本業收入 — active/labour income (``income`` type only), positive",
        schema_extra={"examples": [80000.0]},
    )
    fixed: float = Field(
        ..., description="Fixed-expense magnitude, positive", schema_extra={"examples": [25000.0]}
    )
    floating: float = Field(
        ..., description="Variable-expense magnitude, positive", schema_extra={"examples": [18000.0]}
    )
    loan_interest: float = Field(
        default=0.0,
        description="貸款利息 — loan interest/fee from Loan_Journal, positive",
        schema_extra={"examples": [0.0]},
    )
    operating_net: float = Field(
        ...,
        description="本業淨額 = active_income − fixed − floating − loan_interest, signed",
        schema_extra={"examples": [37000.0]},
    )
    dividend: float = Field(
        ...,
        description="孳息 — passive income (dividends/interest/rent), positive",
        schema_extra={"examples": [3000.0]},
    )
    realized: float = Field(
        ...,
        description="已實現資本利得 from booked 資本利得 journals, signed (loss negative)",
        schema_extra={"examples": [5000.0]},
    )
    unrealized: float = Field(
        ...,
        description="未實現市值變動 — period change in (market value − cost) of holdings, signed",
        schema_extra={"examples": [12000.0]},
    )
    investment_net: float = Field(
        ...,
        description="投資損益合計 = dividend + realized + unrealized, signed",
        schema_extra={"examples": [20000.0]},
    )
    comprehensive_net: float = Field(
        ...,
        description="綜合損益 = operating_net + investment_net, signed",
        schema_extra={"examples": [57000.0]},
    )

    model_config = ConfigDict(json_schema_extra={"example": _POINT_EXAMPLE})


_SUMMARY_EXAMPLE = {
    "active_income": 960000.0,
    "fixed": 300000.0,
    "floating": 216000.0,
    "loan_interest": 0.0,
    "operating_net": 444000.0,
    "dividend": 36000.0,
    "realized": 60000.0,
    "unrealized": 144000.0,
    "investment_net": 240000.0,
    "comprehensive_net": 684000.0,
}


class IncomeStatementSummary(SQLModel):
    active_income: float = Field(
        ..., description="本業收入 across the window, positive", schema_extra={"examples": [960000.0]}
    )
    fixed: float = Field(
        ..., description="Fixed-expense total across the window, positive", schema_extra={"examples": [300000.0]}
    )
    floating: float = Field(
        ..., description="Variable-expense total across the window, positive", schema_extra={"examples": [216000.0]}
    )
    loan_interest: float = Field(
        default=0.0,
        description="貸款利息 total across the window (Loan_Journal interest/fee), positive",
        schema_extra={"examples": [0.0]},
    )
    operating_net: float = Field(
        ..., description="本業淨額 = active_income − fixed − floating − loan_interest across the window", schema_extra={"examples": [444000.0]}
    )
    dividend: float = Field(
        ..., description="孳息 (passive income) total across the window, positive", schema_extra={"examples": [36000.0]}
    )
    realized: float = Field(
        ..., description="已實現資本利得 total across the window, signed", schema_extra={"examples": [60000.0]}
    )
    unrealized: float = Field(
        ..., description="未實現市值變動 across the window, signed", schema_extra={"examples": [144000.0]}
    )
    investment_net: float = Field(
        ..., description="投資損益合計 across the window", schema_extra={"examples": [240000.0]}
    )
    comprehensive_net: float = Field(
        ...,
        description="綜合損益 = operating_net + investment_net across the window",
        schema_extra={"examples": [684000.0]},
    )

    model_config = ConfigDict(json_schema_extra={"example": _SUMMARY_EXAMPLE})


class IncomeStatementReportRead(SQLModel):
    type: Literal["monthly", "yearly"] = Field(
        ..., description="Aggregation granularity", schema_extra={"examples": ["monthly"]}
    )
    points: list[IncomeStatementPoint] = Field(
        ..., description="Time series, oldest first", schema_extra={"examples": [[_POINT_EXAMPLE]]}
    )
    summary: IncomeStatementSummary = Field(
        ..., description="Section totals across the window"
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
