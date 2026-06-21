"""Gift response schema for dashboard view (BE-028)."""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class GiftItem(SQLModel):
    owner: str = Field(
        ...,
        description="Recipient/sender owner name from Account.owner",
        schema_extra={"examples": ["Mom"]},
    )
    amount: float = Field(
        ...,
        description="Summed absolute spending in base currency",
        schema_extra={"examples": [6000.0]},
    )
    rate: float = Field(
        ...,
        description="amount * 100 / 2,200,000 (legacy gift-tax threshold percentage)",
        schema_extra={"examples": [0.27]},
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"owner": "Mom", "amount": 6000.0, "rate": 0.27}}
    )
