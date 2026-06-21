"""AccountBalance snapshot table (Monthly Report domain)."""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


_EXAMPLE = {
    "vesting_month": "202604",
    "id": "BANK-CHASE-01",
    "name": "Chase Checking",
    "balance": 12345.67,
    "fx_code": "USD",
    "fx_rate": 31.5,
    "is_calculate": "Y",
}


class AccountBalance(SQLModel, table=True):
    __tablename__ = "Account_Balance"

    vesting_month: str = Field(..., primary_key=True, description="YYYYMM", schema_extra={"examples": ["202604"]})
    id: str = Field(..., primary_key=True, description="Account business ID", schema_extra={"examples": ["BANK-CHASE-01"]})
    name: str = Field(..., description="Account display name", schema_extra={"examples": ["Chase Checking"]})
    balance: float = Field(..., description="Closing balance in account currency", schema_extra={"examples": [12345.67]})
    fx_code: str = Field(..., description="Currency code", schema_extra={"examples": ["USD"]})
    fx_rate: float = Field(..., description="Exchange rate to base currency", schema_extra={"examples": [31.5]})
    is_calculate: str = Field(..., description="Include in totals (Y/N)", schema_extra={"examples": ["Y"]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class AccountBalanceCreate(SQLModel):
    vesting_month: str = Field(..., description="YYYYMM", schema_extra={"examples": ["202604"]})
    id: str = Field(..., description="Account business ID", schema_extra={"examples": ["BANK-CHASE-01"]})
    name: str = Field(..., description="Account display name", schema_extra={"examples": ["Chase Checking"]})
    balance: float = Field(..., description="Closing balance", schema_extra={"examples": [12345.67]})
    fx_code: str = Field(..., description="Currency code", schema_extra={"examples": ["USD"]})
    fx_rate: float = Field(..., description="Exchange rate", schema_extra={"examples": [31.5]})
    is_calculate: str = Field(..., description="Include in totals (Y/N)", schema_extra={"examples": ["Y"]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class AccountBalanceUpdate(SQLModel):
    name: str | None = Field(default=None, description="Account display name", schema_extra={"examples": ["Chase Checking"]})
    balance: float | None = Field(default=None, description="Closing balance", schema_extra={"examples": [12345.67]})
    fx_code: str | None = Field(default=None, description="Currency code", schema_extra={"examples": ["USD"]})
    fx_rate: float | None = Field(default=None, description="Exchange rate", schema_extra={"examples": [31.5]})
    is_calculate: str | None = Field(default=None, description="Include in totals", schema_extra={"examples": ["N"]})

    model_config = ConfigDict(json_schema_extra={"example": {"balance": 20000.0}})


class AccountBalanceRead(SQLModel):
    vesting_month: str = Field(..., description="YYYYMM", schema_extra={"examples": ["202604"]})
    id: str = Field(..., description="Account business ID", schema_extra={"examples": ["BANK-CHASE-01"]})
    name: str = Field(..., description="Account display name", schema_extra={"examples": ["Chase Checking"]})
    balance: float = Field(..., description="Closing balance", schema_extra={"examples": [12345.67]})
    fx_code: str = Field(..., description="Currency code", schema_extra={"examples": ["USD"]})
    fx_rate: float = Field(..., description="Exchange rate", schema_extra={"examples": [31.5]})
    is_calculate: str = Field(..., description="Include in totals", schema_extra={"examples": ["Y"]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})
