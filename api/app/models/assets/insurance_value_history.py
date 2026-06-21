"""InsuranceValueHistory — user-recorded policy surrender (cash) value over time.

For traditional savings/whole-life policies the surrender value (解約金) is a
known, contractual schedule; the user records it per month here (entered when it
changes, carried forward otherwise). The settlement step reads the latest entry
on or before month-end and uses it as the policy's value, falling back to the
net-premium estimate when no value has been recorded — mirroring how
``StockPriceHistory`` supplies a market price the settlement consumes.
"""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

_EXAMPLE = {
    "insurance_id": "INS-001",
    "vesting_month": "202604",
    "surrender_value": 185000.0,
    "memo": "保單第 6 年度解約金",
}


class InsuranceValueHistory(SQLModel, table=True):
    __tablename__ = "Insurance_Value_History"

    insurance_id: str = Field(
        ..., primary_key=True, description="FK to Insurance.insurance_id", schema_extra={"examples": ["INS-001"]}
    )
    vesting_month: str = Field(
        ..., primary_key=True, description="YYYYMM the value is effective from", schema_extra={"examples": ["202604"]}
    )
    surrender_value: float = Field(
        ..., description="解約金 (cash surrender value) in the policy currency", schema_extra={"examples": [185000.0]}
    )
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["保單第 6 年度解約金"]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class InsuranceValueCreate(SQLModel):
    insurance_id: str = Field(..., description="FK to Insurance.insurance_id", schema_extra={"examples": ["INS-001"]})
    vesting_month: str = Field(..., description="YYYYMM the value is effective from", schema_extra={"examples": ["202604"]})
    surrender_value: float = Field(..., description="解約金 in policy currency", schema_extra={"examples": [185000.0]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["保單第 6 年度解約金"]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class InsuranceValueRead(SQLModel):
    insurance_id: str = Field(..., description="FK to Insurance.insurance_id", schema_extra={"examples": ["INS-001"]})
    vesting_month: str = Field(..., description="YYYYMM the value is effective from", schema_extra={"examples": ["202604"]})
    surrender_value: float = Field(..., description="解約金 in policy currency", schema_extra={"examples": [185000.0]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["保單第 6 年度解約金"]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class InsuranceValueMonthRead(SQLModel):
    """Per-policy view for a month: the recorded value plus context for the form.

    ``surrender_value`` is the latest recorded value on or before the month
    (carried forward); ``recorded`` is False when it was inherited from an
    earlier month or absent entirely, so the UI can flag months needing input.
    """

    insurance_id: str = Field(..., description="Policy business ID", schema_extra={"examples": ["INS-001"]})
    insurance_name: str = Field(..., description="Policy display name", schema_extra={"examples": ["Whole life policy"]})
    surrender_value: float | None = Field(
        default=None,
        description="Latest recorded 解約金 on or before the month, or null when none recorded",
        schema_extra={"examples": [185000.0]},
    )
    vesting_month: str | None = Field(
        default=None,
        description="YYYYMM the surrender_value was recorded for, or null when none",
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
                "insurance_id": "INS-001",
                "insurance_name": "Whole life policy",
                "surrender_value": 185000.0,
                "vesting_month": "202604",
                "recorded": True,
            }
        }
    )
