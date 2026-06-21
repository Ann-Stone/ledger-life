"""EstateValueHistory — user-recorded real-estate market value (估值) over time.

Real-estate market value cannot be auto-fetched (no reliable per-property quote
source), so the user records a periodic appraisal here — from 實價登錄 comparables
or a bank valuation. The settlement step reads the latest entry on or before
month-end and uses it as the property's market value, falling back to cost when
nothing has been recorded. Mirrors ``InsuranceValueHistory`` / ``StockPriceHistory``.
"""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

_EXAMPLE = {
    "estate_id": "EST-001",
    "vesting_month": "202604",
    "market_value": 13800000.0,
    "memo": "同社區 2026Q1 實價登錄估算",
}


class EstateValueHistory(SQLModel, table=True):
    __tablename__ = "Estate_Value_History"

    estate_id: str = Field(
        ..., primary_key=True, description="FK to Estate.estate_id", schema_extra={"examples": ["EST-001"]}
    )
    vesting_month: str = Field(
        ..., primary_key=True, description="YYYYMM the value is effective from", schema_extra={"examples": ["202604"]}
    )
    market_value: float = Field(
        ..., description="Appraised market value in the estate's currency", schema_extra={"examples": [13800000.0]}
    )
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["同社區 2026Q1 實價登錄估算"]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class EstateValueCreate(SQLModel):
    estate_id: str = Field(..., description="FK to Estate.estate_id", schema_extra={"examples": ["EST-001"]})
    vesting_month: str = Field(..., description="YYYYMM the value is effective from", schema_extra={"examples": ["202604"]})
    market_value: float = Field(..., description="Appraised market value in estate currency", schema_extra={"examples": [13800000.0]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["同社區 2026Q1 實價登錄估算"]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class EstateValueRead(SQLModel):
    estate_id: str = Field(..., description="FK to Estate.estate_id", schema_extra={"examples": ["EST-001"]})
    vesting_month: str = Field(..., description="YYYYMM the value is effective from", schema_extra={"examples": ["202604"]})
    market_value: float = Field(..., description="Appraised market value in estate currency", schema_extra={"examples": [13800000.0]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["同社區 2026Q1 實價登錄估算"]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class EstateValueMonthRead(SQLModel):
    """Per-estate view for a month: recorded market value plus context for the form.

    ``market_value`` is the latest recorded value on or before the month (carried
    forward); ``recorded`` is True only when entered in this exact month.
    """

    estate_id: str = Field(..., description="Estate business ID", schema_extra={"examples": ["EST-001"]})
    estate_name: str = Field(..., description="Estate display name", schema_extra={"examples": ["主要住所"]})
    market_value: float | None = Field(
        default=None,
        description="Latest recorded market value on or before the month, or null when none",
        schema_extra={"examples": [13800000.0]},
    )
    vesting_month: str | None = Field(
        default=None,
        description="YYYYMM the market_value was recorded for, or null when none",
        schema_extra={"examples": ["202604"]},
    )
    recorded: bool = Field(
        default=False,
        description="True when a value was recorded in this exact month (not carried forward)",
        schema_extra={"examples": [True]},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estate_id": "EST-001",
                "estate_name": "主要住所",
                "market_value": 13800000.0,
                "vesting_month": "202604",
                "recorded": True,
            }
        }
    )
