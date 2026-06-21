"""Expenditure trend response schemas (Reports domain)."""
from __future__ import annotations

from typing import Literal

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class ExpenditurePoint(SQLModel):
    period: str = Field(
        ...,
        description="YYYYMM for monthly or YYYY for yearly",
        schema_extra={"examples": ["202403"]},
    )
    amount: float = Field(
        ...,
        description="Summed spending in base currency",
        schema_extra={"examples": [45200.0]},
    )

    model_config = ConfigDict(json_schema_extra={"example": {"period": "202403", "amount": 45200.0}})


class ExpenditureTrendRead(SQLModel):
    type: Literal["monthly", "yearly"] = Field(
        ..., description="Aggregation granularity", schema_extra={"examples": ["monthly"]}
    )
    points: list[ExpenditurePoint] = Field(
        ..., description="Time series, oldest first", schema_extra={"examples": [[]]}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "monthly",
                "points": [
                    {"period": "202403", "amount": 45200.0},
                    {"period": "202404", "amount": 38500.0},
                ],
            }
        }
    )
