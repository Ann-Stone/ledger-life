"""Expense insights (年度洞察) response schemas — Reports domain.

Year-over-year change per expense category (this year vs the prior calendar
year) plus the largest individual expense transactions of the year. Amounts are
FX-converted; only Fixed/Floating rows count.
"""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

_YOY_EXAMPLE = {
    "code": "E01",
    "name": "餐飲",
    "type": "Floating",
    "current": 192000.0,
    "previous": 168000.0,
    "delta": 24000.0,
    "yoy_rate": 0.1429,
}


class YoYRow(SQLModel):
    code: str = Field(..., description="Category code (action_main)", schema_extra={"examples": ["E01"]})
    name: str = Field(..., description="Category display name", schema_extra={"examples": ["餐飲"]})
    type: str = Field(..., description="Code type: Fixed or Floating", schema_extra={"examples": ["Floating"]})
    current: float = Field(..., description="This year's actual expense", schema_extra={"examples": [192000.0]})
    previous: float = Field(..., description="Prior year's actual expense", schema_extra={"examples": [168000.0]})
    delta: float = Field(..., description="current - previous", schema_extra={"examples": [24000.0]})
    yoy_rate: float = Field(
        ..., description="(current - previous) / previous (0 when previous == 0)", schema_extra={"examples": [0.1429]}
    )

    model_config = ConfigDict(json_schema_extra={"example": _YOY_EXAMPLE})


_TXN_EXAMPLE = {
    "date": "20260815",
    "category": "旅遊",
    "amount": 85000.0,
    "pay_way": "Chase Sapphire",
    "note": "日本機票",
}


class LargeTxn(SQLModel):
    date: str = Field(..., description="Transaction date YYYYMMDD", schema_extra={"examples": ["20260815"]})
    category: str = Field(..., description="Category name (action_main)", schema_extra={"examples": ["旅遊"]})
    amount: float = Field(
        ..., description="Expense magnitude in base currency, positive", schema_extra={"examples": [85000.0]}
    )
    pay_way: str = Field(..., description="Account or credit-card name", schema_extra={"examples": ["Chase Sapphire"]})
    note: str | None = Field(default=None, description="Free-form note", schema_extra={"examples": ["日本機票"]})

    model_config = ConfigDict(json_schema_extra={"example": _TXN_EXAMPLE})


class ExpenseInsightsRead(SQLModel):
    year: str = Field(..., description="Calendar year YYYY", schema_extra={"examples": ["2026"]})
    yoy: list[YoYRow] = Field(
        ..., description="Per-category YoY, ordered by |delta| descending", schema_extra={"examples": [[_YOY_EXAMPLE]]}
    )
    largest: list[LargeTxn] = Field(
        ..., description="Largest expense transactions, amount descending", schema_extra={"examples": [[_TXN_EXAMPLE]]}
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"year": "2026", "yoy": [_YOY_EXAMPLE], "largest": [_TXN_EXAMPLE]}}
    )
