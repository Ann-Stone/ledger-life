"""LoanBalance snapshot table (Monthly Report domain)."""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


_EXAMPLE = {
    "vesting_month": "202604",
    "id": "LN-001",
    "name": "Mortgage",
    "balance": -250000.0,
    "cost": 250000.0,
    "fx_code": "TWD",
    "fx_rate": 1.0,
}


class LoanBalance(SQLModel, table=True):
    __tablename__ = "Loan_Balance"

    vesting_month: str = Field(..., primary_key=True, description="YYYYMM", schema_extra={"examples": ["202604"]})
    id: str = Field(..., primary_key=True, description="Loan ID", schema_extra={"examples": ["LN-001"]})
    name: str = Field(..., description="Loan display name", schema_extra={"examples": ["Mortgage"]})
    balance: float = Field(..., description="Outstanding balance (negative = liability)", schema_extra={"examples": [-250000.0]})
    cost: float = Field(..., description="Original loan amount", schema_extra={"examples": [250000.0]})
    fx_code: str = Field(..., description="Currency code", schema_extra={"examples": ["TWD"]})
    fx_rate: float = Field(..., description="Exchange rate to base currency", schema_extra={"examples": [1.0]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class LoanBalanceCreate(SQLModel):
    vesting_month: str = Field(..., description="YYYYMM", schema_extra={"examples": ["202604"]})
    id: str = Field(..., description="Loan ID", schema_extra={"examples": ["LN-001"]})
    name: str = Field(..., description="Loan display name", schema_extra={"examples": ["Mortgage"]})
    balance: float = Field(..., description="Outstanding balance", schema_extra={"examples": [-250000.0]})
    cost: float = Field(..., description="Original loan amount", schema_extra={"examples": [250000.0]})
    fx_code: str = Field(..., description="Currency code", schema_extra={"examples": ["TWD"]})
    fx_rate: float = Field(..., description="Exchange rate to base currency", schema_extra={"examples": [1.0]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class LoanBalanceUpdate(SQLModel):
    name: str | None = Field(default=None, description="Loan display name", schema_extra={"examples": ["Mortgage"]})
    balance: float | None = Field(default=None, description="Outstanding balance", schema_extra={"examples": [-240000.0]})
    cost: float | None = Field(default=None, description="Original loan amount", schema_extra={"examples": [250000.0]})

    model_config = ConfigDict(json_schema_extra={"example": {"balance": -240000.0}})


class LoanBalanceRead(SQLModel):
    vesting_month: str = Field(..., description="YYYYMM", schema_extra={"examples": ["202604"]})
    id: str = Field(..., description="Loan ID", schema_extra={"examples": ["LN-001"]})
    name: str = Field(..., description="Loan display name", schema_extra={"examples": ["Mortgage"]})
    balance: float = Field(..., description="Outstanding balance", schema_extra={"examples": [-250000.0]})
    cost: float = Field(..., description="Original loan amount", schema_extra={"examples": [250000.0]})
    fx_code: str = Field(..., description="Currency code", schema_extra={"examples": ["TWD"]})
    fx_rate: float = Field(..., description="Exchange rate to base currency", schema_extra={"examples": [1.0]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})
