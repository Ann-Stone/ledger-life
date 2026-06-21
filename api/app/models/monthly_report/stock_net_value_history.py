"""StockNetValueHistory snapshot table (Monthly Report domain).

Note: legacy model had a typo `__tablestock_name__`; this module uses the
correct `__tablename__`.
"""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


_EXAMPLE = {
    "vesting_month": "202604",
    "id": "STK-H-001",
    "asset_id": "AC-STK-001",
    "stock_code": "AAPL",
    "stock_name": "Apple Inc.",
    "amount": 100.0,
    "price": 180.50,
    "cost": 15000.0,
    "fx_code": "USD",
    "fx_rate": 31.5,
}


class StockNetValueHistory(SQLModel, table=True):
    __tablename__ = "Stock_Net_Value_History"

    vesting_month: str = Field(..., primary_key=True, description="YYYYMM", schema_extra={"examples": ["202604"]})
    id: str = Field(..., primary_key=True, description="Holding ID", schema_extra={"examples": ["STK-H-001"]})
    asset_id: str = Field(..., primary_key=True, description="Asset category ID", schema_extra={"examples": ["AC-STK-001"]})
    stock_code: str = Field(..., description="Ticker symbol", schema_extra={"examples": ["AAPL"]})
    stock_name: str = Field(..., description="Stock display name", schema_extra={"examples": ["Apple Inc."]})
    amount: float = Field(..., description="Holding quantity", schema_extra={"examples": [100.0]})
    price: float = Field(..., description="Closing price", schema_extra={"examples": [180.50]})
    cost: float = Field(..., description="Acquisition cost (base currency)", schema_extra={"examples": [15000.0]})
    fx_code: str = Field(..., description="Currency code", schema_extra={"examples": ["USD"]})
    fx_rate: float = Field(..., description="Exchange rate", schema_extra={"examples": [31.5]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class StockNetValueHistoryCreate(SQLModel):
    vesting_month: str = Field(..., description="YYYYMM", schema_extra={"examples": ["202604"]})
    id: str = Field(..., description="Holding ID", schema_extra={"examples": ["STK-H-001"]})
    asset_id: str = Field(..., description="Asset category ID", schema_extra={"examples": ["AC-STK-001"]})
    stock_code: str = Field(..., description="Ticker symbol", schema_extra={"examples": ["AAPL"]})
    stock_name: str = Field(..., description="Stock name", schema_extra={"examples": ["Apple Inc."]})
    amount: float = Field(..., description="Holding quantity", schema_extra={"examples": [100.0]})
    price: float = Field(..., description="Closing price", schema_extra={"examples": [180.50]})
    cost: float = Field(..., description="Acquisition cost", schema_extra={"examples": [15000.0]})
    fx_code: str = Field(..., description="Currency code", schema_extra={"examples": ["USD"]})
    fx_rate: float = Field(..., description="Exchange rate", schema_extra={"examples": [31.5]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class StockNetValueHistoryUpdate(SQLModel):
    stock_code: str | None = Field(default=None, description="Ticker symbol", schema_extra={"examples": ["AAPL"]})
    stock_name: str | None = Field(default=None, description="Stock name", schema_extra={"examples": ["Apple Inc."]})
    amount: float | None = Field(default=None, description="Holding quantity", schema_extra={"examples": [100.0]})
    price: float | None = Field(default=None, description="Closing price", schema_extra={"examples": [180.50]})
    cost: float | None = Field(default=None, description="Acquisition cost", schema_extra={"examples": [15000.0]})
    fx_code: str | None = Field(default=None, description="Currency code", schema_extra={"examples": ["USD"]})
    fx_rate: float | None = Field(default=None, description="Exchange rate", schema_extra={"examples": [31.5]})

    model_config = ConfigDict(json_schema_extra={"example": {"price": 185.0}})


class StockNetValueHistoryRead(SQLModel):
    vesting_month: str = Field(..., description="YYYYMM", schema_extra={"examples": ["202604"]})
    id: str = Field(..., description="Holding ID", schema_extra={"examples": ["STK-H-001"]})
    asset_id: str = Field(..., description="Asset category ID", schema_extra={"examples": ["AC-STK-001"]})
    stock_code: str = Field(..., description="Ticker symbol", schema_extra={"examples": ["AAPL"]})
    stock_name: str = Field(..., description="Stock name", schema_extra={"examples": ["Apple Inc."]})
    amount: float = Field(..., description="Holding quantity", schema_extra={"examples": [100.0]})
    price: float = Field(..., description="Closing price", schema_extra={"examples": [180.50]})
    cost: float = Field(..., description="Acquisition cost", schema_extra={"examples": [15000.0]})
    fx_code: str = Field(..., description="Currency code", schema_extra={"examples": ["USD"]})
    fx_rate: float = Field(..., description="Exchange rate", schema_extra={"examples": [31.5]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})
