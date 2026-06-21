"""StockPriceHistory model — daily OHLC snapshot per ticker."""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


_EXAMPLE = {
    "stock_code": "AAPL",
    "fetch_date": "20260418",
    "open_price": 180.0,
    "highest_price": 182.5,
    "lowest_price": 179.2,
    "close_price": 181.8,
}


class StockPriceHistory(SQLModel, table=True):
    __tablename__ = "Stock_Price_History"

    stock_code: str = Field(..., primary_key=True, description="Ticker symbol", schema_extra={"examples": ["AAPL"]})
    fetch_date: str = Field(..., primary_key=True, description="YYYYMMDD", schema_extra={"examples": ["20260418"]})
    open_price: float = Field(..., description="Open price", schema_extra={"examples": [180.0]})
    highest_price: float = Field(..., description="Daily high", schema_extra={"examples": [182.5]})
    lowest_price: float = Field(..., description="Daily low", schema_extra={"examples": [179.2]})
    close_price: float = Field(..., description="Close price", schema_extra={"examples": [181.8]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class StockPriceHistoryCreate(SQLModel):
    stock_code: str = Field(..., description="Ticker symbol", schema_extra={"examples": ["AAPL"]})
    fetch_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20260418"]})
    open_price: float = Field(..., description="Open price", schema_extra={"examples": [180.0]})
    highest_price: float = Field(..., description="Daily high", schema_extra={"examples": [182.5]})
    lowest_price: float = Field(..., description="Daily low", schema_extra={"examples": [179.2]})
    close_price: float = Field(..., description="Close price", schema_extra={"examples": [181.8]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class StockPriceHistoryUpdate(SQLModel):
    open_price: float | None = Field(default=None, description="Open price", schema_extra={"examples": [180.0]})
    highest_price: float | None = Field(default=None, description="Daily high", schema_extra={"examples": [182.5]})
    lowest_price: float | None = Field(default=None, description="Daily low", schema_extra={"examples": [179.2]})
    close_price: float | None = Field(default=None, description="Close price", schema_extra={"examples": [181.8]})

    model_config = ConfigDict(json_schema_extra={"example": {"close_price": 181.8}})


class StockPriceHistoryRead(SQLModel):
    stock_code: str = Field(..., description="Ticker symbol", schema_extra={"examples": ["AAPL"]})
    fetch_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20260418"]})
    open_price: float = Field(..., description="Open price", schema_extra={"examples": [180.0]})
    highest_price: float = Field(..., description="Daily high", schema_extra={"examples": [182.5]})
    lowest_price: float = Field(..., description="Daily low", schema_extra={"examples": [179.2]})
    close_price: float = Field(..., description="Close price", schema_extra={"examples": [181.8]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})
