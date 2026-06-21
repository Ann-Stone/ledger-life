"""Stock price DTOs (Monthly Report domain).

The persistent table model lives in ``app.models.dashboard.stock_price_history``;
this module defines only request/response schemas used by the monthly_report
stock-price endpoints (BE-018).
"""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


_PRICE_EXAMPLE = {
    "stock_code": "AAPL",
    "fetch_date": "20260418",
    "open_price": 180.0,
    "highest_price": 182.5,
    "lowest_price": 179.2,
    "close_price": 181.8,
}


class StockPriceCreate(SQLModel):
    stock_code: str = Field(
        ..., description="Ticker symbol", schema_extra={"examples": ["AAPL"]}
    )
    fetch_date: str = Field(
        ..., description="YYYYMMDD", schema_extra={"examples": ["20260418"]}
    )
    open_price: float = Field(
        ..., description="Open price", schema_extra={"examples": [180.0]}
    )
    highest_price: float = Field(
        ..., description="Daily high", schema_extra={"examples": [182.5]}
    )
    lowest_price: float = Field(
        ..., description="Daily low", schema_extra={"examples": [179.2]}
    )
    close_price: float = Field(
        ..., description="Close price (overwritten when trigger_yfinance is True)",
        schema_extra={"examples": [181.8]},
    )
    trigger_yfinance: bool = Field(
        default=False,
        description="When True, fetch close price from yfinance and overwrite close_price.",
        schema_extra={"examples": [False]},
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {**_PRICE_EXAMPLE, "trigger_yfinance": False}}
    )


class StockPriceRead(SQLModel):
    stock_code: str = Field(
        ..., description="Ticker symbol", schema_extra={"examples": ["AAPL"]}
    )
    fetch_date: str = Field(
        ..., description="YYYYMMDD", schema_extra={"examples": ["20260418"]}
    )
    open_price: float = Field(
        ..., description="Open price", schema_extra={"examples": [180.0]}
    )
    highest_price: float = Field(
        ..., description="Daily high", schema_extra={"examples": [182.5]}
    )
    lowest_price: float = Field(
        ..., description="Daily low", schema_extra={"examples": [179.2]}
    )
    close_price: float = Field(
        ..., description="Close price", schema_extra={"examples": [181.8]}
    )

    model_config = ConfigDict(json_schema_extra={"example": _PRICE_EXAMPLE})


class StockPriceMonthRead(SQLModel):
    stock_code: str = Field(
        ..., description="Ticker symbol", schema_extra={"examples": ["AAPL"]}
    )
    stock_name: str = Field(
        ..., description="Stock display name", schema_extra={"examples": ["Apple Inc."]}
    )
    close_price: float | None = Field(
        default=None,
        description=(
            "Close price of the most recent in-month row, or null when the "
            "requested month has no price data (signals a fetch is needed)."
        ),
        schema_extra={"examples": [181.8]},
    )
    fetch_date: str | None = Field(
        default=None,
        description=(
            "YYYYMMDD of the row the close_price came from, or null when the "
            "month has no price data."
        ),
        schema_extra={"examples": ["20260430"]},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "stock_code": "AAPL",
                "stock_name": "Apple Inc.",
                "close_price": 181.8,
                "fetch_date": "20260430",
            }
        }
    )
