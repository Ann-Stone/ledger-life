"""Settlement result schema (Monthly Report domain, BE-019)."""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


_EXAMPLE = {
    "vesting_month": "202604",
    "estate_rows": 1,
    "insurance_rows": 1,
    "loan_rows": 1,
    "stock_rows": 2,
    "account_rows": 4,
    "credit_card_rows": 2,
}


class SettlementResult(SQLModel):
    vesting_month: str = Field(
        ..., description="Settled vesting month (YYYYMM)", schema_extra={"examples": ["202604"]}
    )
    estate_rows: int = Field(
        ..., description="Estate snapshot rows inserted", schema_extra={"examples": [1]}
    )
    insurance_rows: int = Field(
        ..., description="Insurance snapshot rows inserted", schema_extra={"examples": [1]}
    )
    loan_rows: int = Field(
        ..., description="Loan snapshot rows inserted", schema_extra={"examples": [1]}
    )
    stock_rows: int = Field(
        ..., description="Stock snapshot rows inserted (skips zero-amount holdings)",
        schema_extra={"examples": [2]},
    )
    account_rows: int = Field(
        ..., description="AccountBalance rows recomputed for the month",
        schema_extra={"examples": [4]},
    )
    credit_card_rows: int = Field(
        ..., description="CreditCardBalance rows recomputed for the month",
        schema_extra={"examples": [2]},
    )

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})
