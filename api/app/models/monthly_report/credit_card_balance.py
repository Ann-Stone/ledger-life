"""CreditCardBalance snapshot table (Monthly Report domain)."""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


_EXAMPLE = {
    "vesting_month": "202604",
    "id": "CC-VISA-01",
    "name": "Chase Sapphire",
    "balance": -2500.0,
    "fx_rate": 31.5,
}


class CreditCardBalance(SQLModel, table=True):
    __tablename__ = "Credit_Card_Balance"

    vesting_month: str = Field(..., primary_key=True, description="YYYYMM", schema_extra={"examples": ["202604"]})
    id: str = Field(..., primary_key=True, description="Credit card business ID", schema_extra={"examples": ["CC-VISA-01"]})
    name: str = Field(..., description="Card display name", schema_extra={"examples": ["Chase Sapphire"]})
    balance: float = Field(..., description="Outstanding balance (negative = liability)", schema_extra={"examples": [-2500.0]})
    fx_rate: float = Field(..., description="Exchange rate to base currency", schema_extra={"examples": [31.5]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class CreditCardBalanceCreate(SQLModel):
    vesting_month: str = Field(..., description="YYYYMM", schema_extra={"examples": ["202604"]})
    id: str = Field(..., description="Credit card business ID", schema_extra={"examples": ["CC-VISA-01"]})
    name: str = Field(..., description="Card display name", schema_extra={"examples": ["Chase Sapphire"]})
    balance: float = Field(..., description="Outstanding balance", schema_extra={"examples": [-2500.0]})
    fx_rate: float = Field(..., description="Exchange rate", schema_extra={"examples": [31.5]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class CreditCardBalanceUpdate(SQLModel):
    name: str | None = Field(default=None, description="Card display name", schema_extra={"examples": ["Chase Sapphire"]})
    balance: float | None = Field(default=None, description="Outstanding balance", schema_extra={"examples": [-2500.0]})
    fx_rate: float | None = Field(default=None, description="Exchange rate", schema_extra={"examples": [31.5]})

    model_config = ConfigDict(json_schema_extra={"example": {"balance": -3000.0}})


class CreditCardBalanceRead(SQLModel):
    vesting_month: str = Field(..., description="YYYYMM", schema_extra={"examples": ["202604"]})
    id: str = Field(..., description="Credit card business ID", schema_extra={"examples": ["CC-VISA-01"]})
    name: str = Field(..., description="Card display name", schema_extra={"examples": ["Chase Sapphire"]})
    balance: float = Field(..., description="Outstanding balance", schema_extra={"examples": [-2500.0]})
    fx_rate: float = Field(..., description="Exchange rate", schema_extra={"examples": [31.5]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})
