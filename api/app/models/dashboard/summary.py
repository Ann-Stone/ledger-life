"""Dashboard summary response schemas (BE-026)."""
from __future__ import annotations

from enum import Enum

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class SummaryType(str, Enum):
    spending = "spending"
    freedom_ratio = "freedom_ratio"
    asset_debt_trend = "asset_debt_trend"
    work_freedom_ratio = "work_freedom_ratio"


_BREAKDOWN_EXAMPLE = {
    "accounts": 500000.0,
    "stocks": 320000.0,
    "estates": 480000.0,
    "insurances": 24000.0,
    "loans": -240000.0,
    "cards": -3000.0,
}


class SummaryPoint(SQLModel):
    period: str = Field(..., description="YYYYMM", schema_extra={"examples": ["202403"]})
    value: float = Field(
        ...,
        description="Aggregated value for the period",
        schema_extra={"examples": [12345.67]},
    )
    breakdown: dict[str, float] | None = Field(
        default=None,
        description=(
            "Optional per-category contributions. When present, the sum of the "
            "breakdown values equals `value` within rounding tolerance. Populated "
            "for `asset_debt_trend` (keys: accounts, stocks, estates, insurances, "
            "loans, cards), `freedom_ratio` (keys: income, fixed_expenses), and "
            "`work_freedom_ratio` (keys: passive, active). Null for variants that "
            "do not expose a per-category breakdown."
        ),
        schema_extra={"examples": [_BREAKDOWN_EXAMPLE]},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "period": "202403",
                "value": 1081000.0,
                "breakdown": _BREAKDOWN_EXAMPLE,
            }
        }
    )


class SummaryRead(SQLModel):
    type: SummaryType = Field(
        ..., description="Summary variant", schema_extra={"examples": ["spending"]}
    )
    points: list[SummaryPoint] = Field(
        ..., description="Time series, oldest first", schema_extra={"examples": [[]]}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "asset_debt_trend",
                "points": [
                    {
                        "period": "202301",
                        "value": 1050000.0,
                        "breakdown": {
                            "accounts": 480000.0,
                            "stocks": 310000.0,
                            "estates": 470000.0,
                            "insurances": 23000.0,
                            "loans": -230000.0,
                            "cards": -3000.0,
                        },
                    },
                    {
                        "period": "202302",
                        "value": 1081000.0,
                        "breakdown": _BREAKDOWN_EXAMPLE,
                    },
                ],
            }
        }
    )
