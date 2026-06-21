"""Asset composition response schemas (Reports domain)."""
from __future__ import annotations

from typing import Literal

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class AssetShare(SQLModel):
    type: Literal["stocks", "estates", "insurances", "accounts", "other"] = Field(
        ..., description="Asset bucket", schema_extra={"examples": ["stocks"]}
    )
    amount: float = Field(
        ..., description="Amount in base currency", schema_extra={"examples": [200000.0]}
    )
    share: float = Field(
        ..., description="Percentage 0-100", schema_extra={"examples": [32.5]}
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"type": "stocks", "amount": 200000.0, "share": 32.5}}
    )


class AssetBreakdownRead(SQLModel):
    total: float = Field(
        ..., description="Total asset value in base currency", schema_extra={"examples": [615384.62]}
    )
    items: list[AssetShare] = Field(
        ..., description="Per-bucket share, sums to 100% within rounding", schema_extra={"examples": [[]]}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 615384.62,
                "items": [
                    {"type": "stocks", "amount": 200000.0, "share": 32.5},
                    {"type": "accounts", "amount": 415384.62, "share": 67.5},
                ],
            }
        }
    )
