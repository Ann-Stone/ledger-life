"""EstateNetValueHistory snapshot table (Monthly Report domain)."""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


_EXAMPLE = {
    "vesting_month": "202604",
    "id": "EST-001",
    "asset_id": "AC-REAL-001",
    "name": "Condo",
    "market_value": 500000.0,
    "cost": 420000.0,
    "estate_status": "hold",
    "fx_code": "TWD",
    "fx_rate": 1.0,
}


class EstateNetValueHistory(SQLModel, table=True):
    __tablename__ = "Estate_Net_Value_History"

    vesting_month: str = Field(..., primary_key=True, description="YYYYMM", schema_extra={"examples": ["202604"]})
    id: str = Field(..., primary_key=True, description="Estate ID", schema_extra={"examples": ["EST-001"]})
    asset_id: str = Field(..., primary_key=True, description="Asset category ID", schema_extra={"examples": ["AC-REAL-001"]})
    name: str = Field(..., description="Estate display name", schema_extra={"examples": ["Condo"]})
    market_value: float = Field(..., description="Market value snapshot", schema_extra={"examples": [500000.0]})
    cost: float = Field(..., description="Acquisition cost", schema_extra={"examples": [420000.0]})
    estate_status: str = Field(..., description="Status (hold / sold / ...)", schema_extra={"examples": ["hold"]})
    fx_code: str = Field(..., description="Currency code", schema_extra={"examples": ["TWD"]})
    fx_rate: float = Field(..., description="Exchange rate to base currency", schema_extra={"examples": [1.0]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class EstateNetValueHistoryCreate(SQLModel):
    vesting_month: str = Field(..., description="YYYYMM", schema_extra={"examples": ["202604"]})
    id: str = Field(..., description="Estate ID", schema_extra={"examples": ["EST-001"]})
    asset_id: str = Field(..., description="Asset category ID", schema_extra={"examples": ["AC-REAL-001"]})
    name: str = Field(..., description="Estate display name", schema_extra={"examples": ["Condo"]})
    market_value: float = Field(..., description="Market value", schema_extra={"examples": [500000.0]})
    cost: float = Field(..., description="Acquisition cost", schema_extra={"examples": [420000.0]})
    estate_status: str = Field(..., description="Status", schema_extra={"examples": ["hold"]})
    fx_code: str = Field(..., description="Currency code", schema_extra={"examples": ["TWD"]})
    fx_rate: float = Field(..., description="Exchange rate to base currency", schema_extra={"examples": [1.0]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class EstateNetValueHistoryUpdate(SQLModel):
    name: str | None = Field(default=None, description="Estate display name", schema_extra={"examples": ["Condo"]})
    market_value: float | None = Field(default=None, description="Market value", schema_extra={"examples": [510000.0]})
    cost: float | None = Field(default=None, description="Acquisition cost", schema_extra={"examples": [420000.0]})
    estate_status: str | None = Field(default=None, description="Status", schema_extra={"examples": ["sold"]})

    model_config = ConfigDict(json_schema_extra={"example": {"market_value": 510000.0}})


class EstateNetValueHistoryRead(SQLModel):
    vesting_month: str = Field(..., description="YYYYMM", schema_extra={"examples": ["202604"]})
    id: str = Field(..., description="Estate ID", schema_extra={"examples": ["EST-001"]})
    asset_id: str = Field(..., description="Asset category ID", schema_extra={"examples": ["AC-REAL-001"]})
    name: str = Field(..., description="Estate display name", schema_extra={"examples": ["Condo"]})
    market_value: float = Field(..., description="Market value", schema_extra={"examples": [500000.0]})
    cost: float = Field(..., description="Acquisition cost", schema_extra={"examples": [420000.0]})
    estate_status: str = Field(..., description="Status", schema_extra={"examples": ["hold"]})
    fx_code: str = Field(..., description="Currency code", schema_extra={"examples": ["TWD"]})
    fx_rate: float = Field(..., description="Exchange rate to base currency", schema_extra={"examples": [1.0]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})
