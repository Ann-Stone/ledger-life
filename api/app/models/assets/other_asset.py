"""OtherAsset (asset category) model."""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


_EXAMPLE = {
    "asset_id": "AC-STK-001",
    "asset_name": "US equities",
    "asset_type": "stock",
    "in_use": "Y",
    "asset_index": 1,
}


class OtherAsset(SQLModel, table=True):
    __tablename__ = "Other_Asset"

    asset_id: str = Field(..., primary_key=True, description="Asset category business ID", schema_extra={"examples": ["AC-STK-001"]})
    asset_name: str = Field(..., description="Asset category display name", schema_extra={"examples": ["US equities"]})
    asset_type: str = Field(..., description="Asset category type (stock / insurance / estate / loan / other)", schema_extra={"examples": ["stock"]})
    in_use: str = Field(..., description="Active flag (Y/N)", schema_extra={"examples": ["Y"]})
    asset_index: int = Field(..., description="Dropdown order, ORDER BY ASC", schema_extra={"examples": [1]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class OtherAssetCreate(SQLModel):
    asset_id: str = Field(..., description="Asset category business ID", schema_extra={"examples": ["AC-STK-001"]})
    asset_name: str = Field(..., description="Display name", schema_extra={"examples": ["US equities"]})
    asset_type: str = Field(..., description="Asset category type", schema_extra={"examples": ["stock"]})
    in_use: str = Field(..., description="Active flag", schema_extra={"examples": ["Y"]})
    asset_index: int | None = Field(default=None, description="Display order; server assigns max+1 if omitted", schema_extra={"examples": [1]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class OtherAssetUpdate(SQLModel):
    asset_name: str | None = Field(default=None, description="Display name", schema_extra={"examples": ["US equities"]})
    asset_type: str | None = Field(default=None, description="Asset category type", schema_extra={"examples": ["stock"]})
    in_use: str | None = Field(default=None, description="Active flag", schema_extra={"examples": ["N"]})
    asset_index: int | None = Field(default=None, description="Dropdown order", schema_extra={"examples": [2]})

    model_config = ConfigDict(json_schema_extra={"example": {"in_use": "N"}})


class OtherAssetRead(SQLModel):
    asset_id: str = Field(..., description="Asset category business ID", schema_extra={"examples": ["AC-STK-001"]})
    asset_name: str = Field(..., description="Display name", schema_extra={"examples": ["US equities"]})
    asset_type: str = Field(..., description="Asset category type", schema_extra={"examples": ["stock"]})
    in_use: str = Field(..., description="Active flag", schema_extra={"examples": ["Y"]})
    asset_index: int = Field(..., description="Dropdown order", schema_extra={"examples": [1]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class OtherAssetItem(SQLModel):
    asset_type: str = Field(..., description="Distinct asset_type value", schema_extra={"examples": ["stock"]})

    model_config = ConfigDict(json_schema_extra={"example": {"asset_type": "stock"}})
