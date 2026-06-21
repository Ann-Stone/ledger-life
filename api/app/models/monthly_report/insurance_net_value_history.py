"""InsuranceNetValueHistory snapshot table (Monthly Report domain)."""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


_EXAMPLE = {
    "vesting_month": "202604",
    "id": "INS-001",
    "asset_id": "AC-INS-001",
    "name": "Whole life policy",
    "surrender_value": 25000.0,
    "cost": 20000.0,
    "fx_code": "USD",
    "fx_rate": 31.5,
}


class InsuranceNetValueHistory(SQLModel, table=True):
    __tablename__ = "Insurance_Net_Value_History"

    vesting_month: str = Field(..., primary_key=True, description="YYYYMM", schema_extra={"examples": ["202604"]})
    id: str = Field(..., primary_key=True, description="Policy ID", schema_extra={"examples": ["INS-001"]})
    asset_id: str = Field(..., primary_key=True, description="Asset category ID", schema_extra={"examples": ["AC-INS-001"]})
    name: str = Field(..., description="Policy display name", schema_extra={"examples": ["Whole life policy"]})
    surrender_value: float = Field(..., description="Surrender value snapshot", schema_extra={"examples": [25000.0]})
    cost: float = Field(..., description="Cumulative premium paid", schema_extra={"examples": [20000.0]})
    fx_code: str = Field(..., description="Currency code", schema_extra={"examples": ["USD"]})
    fx_rate: float = Field(..., description="Exchange rate", schema_extra={"examples": [31.5]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class InsuranceNetValueHistoryCreate(SQLModel):
    vesting_month: str = Field(..., description="YYYYMM", schema_extra={"examples": ["202604"]})
    id: str = Field(..., description="Policy ID", schema_extra={"examples": ["INS-001"]})
    asset_id: str = Field(..., description="Asset category ID", schema_extra={"examples": ["AC-INS-001"]})
    name: str = Field(..., description="Policy display name", schema_extra={"examples": ["Whole life policy"]})
    surrender_value: float = Field(..., description="Surrender value", schema_extra={"examples": [25000.0]})
    cost: float = Field(..., description="Cumulative premium paid", schema_extra={"examples": [20000.0]})
    fx_code: str = Field(..., description="Currency code", schema_extra={"examples": ["USD"]})
    fx_rate: float = Field(..., description="Exchange rate", schema_extra={"examples": [31.5]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class InsuranceNetValueHistoryUpdate(SQLModel):
    name: str | None = Field(default=None, description="Policy display name", schema_extra={"examples": ["Whole life policy"]})
    surrender_value: float | None = Field(default=None, description="Surrender value", schema_extra={"examples": [25000.0]})
    cost: float | None = Field(default=None, description="Cumulative premium", schema_extra={"examples": [20000.0]})
    fx_code: str | None = Field(default=None, description="Currency code", schema_extra={"examples": ["USD"]})
    fx_rate: float | None = Field(default=None, description="Exchange rate", schema_extra={"examples": [31.5]})

    model_config = ConfigDict(json_schema_extra={"example": {"surrender_value": 26000.0}})


class InsuranceNetValueHistoryRead(SQLModel):
    vesting_month: str = Field(..., description="YYYYMM", schema_extra={"examples": ["202604"]})
    id: str = Field(..., description="Policy ID", schema_extra={"examples": ["INS-001"]})
    asset_id: str = Field(..., description="Asset category ID", schema_extra={"examples": ["AC-INS-001"]})
    name: str = Field(..., description="Policy display name", schema_extra={"examples": ["Whole life policy"]})
    surrender_value: float = Field(..., description="Surrender value", schema_extra={"examples": [25000.0]})
    cost: float = Field(..., description="Cumulative premium", schema_extra={"examples": [20000.0]})
    fx_code: str = Field(..., description="Currency code", schema_extra={"examples": ["USD"]})
    fx_rate: float = Field(..., description="Exchange rate", schema_extra={"examples": [31.5]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})
