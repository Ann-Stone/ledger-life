"""HousePriceIndex — 內政部 residential price index (住宅價格指數) series cache.

External market-reference data (like StockPriceHistory): a transaction-based,
repeat-sales quarterly index used to *suggest* a real-estate market value
(cost × index growth since purchase). Refreshed best-effort from data.gov.tw
open data. ``region`` keeps the series multi-region-ready (v1 uses one configured
region); ``quarter`` is a Gregorian key like ``2024Q1`` (ROC 期別 is converted on import).
"""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

_EXAMPLE = {"region": "臺北市全市", "quarter": "2024Q1", "index_value": 137.73}


class HousePriceIndex(SQLModel, table=True):
    __tablename__ = "House_Price_Index"

    region: str = Field(
        ..., primary_key=True, description="Index region label", schema_extra={"examples": ["臺北市全市"]}
    )
    quarter: str = Field(
        ..., primary_key=True, description="Gregorian quarter key, e.g. 2024Q1", schema_extra={"examples": ["2024Q1"]}
    )
    index_value: float = Field(
        ..., description="Quarterly residential price index value", schema_extra={"examples": [137.73]}
    )

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class HousePriceIndexRead(SQLModel):
    region: str = Field(..., description="Index region label", schema_extra={"examples": ["臺北市全市"]})
    quarter: str = Field(..., description="Gregorian quarter key", schema_extra={"examples": ["2024Q1"]})
    index_value: float = Field(..., description="Quarterly index value", schema_extra={"examples": [137.73]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class IndexRefreshResult(SQLModel):
    region: str = Field(..., description="Region refreshed", schema_extra={"examples": ["臺北市全市"]})
    upserted: int = Field(..., description="Number of quarters inserted/updated", schema_extra={"examples": [48]})
    ok: bool = Field(..., description="False when the fetch failed and existing data was kept", schema_extra={"examples": [True]})

    model_config = ConfigDict(
        json_schema_extra={"example": {"region": "臺北市全市", "upserted": 48, "ok": True}}
    )


class EstateValueSuggestion(SQLModel):
    estate_id: str = Field(..., description="Estate business ID", schema_extra={"examples": ["EST-001"]})
    estate_name: str = Field(..., description="Estate display name", schema_extra={"examples": ["主要住所"]})
    cost: float = Field(..., description="Acquisition cost (sum of estate journals)", schema_extra={"examples": [10000000.0]})
    suggested_market_value: float | None = Field(
        default=None,
        description="cost × (current index / obtain-quarter index); null when the index is unavailable",
        schema_extra={"examples": [13773000.0]},
    )
    region: str = Field(..., description="Index region used for the suggestion", schema_extra={"examples": ["臺北市全市"]})
    obtain_quarter: str | None = Field(
        default=None, description="Quarter of the estate's obtain_date", schema_extra={"examples": ["2020Q1"]}
    )
    current_quarter: str | None = Field(
        default=None, description="Latest index quarter at or before the report month", schema_extra={"examples": ["2024Q1"]}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estate_id": "EST-001",
                "estate_name": "主要住所",
                "cost": 10000000.0,
                "suggested_market_value": 13773000.0,
                "region": "臺北市全市",
                "obtain_quarter": "2020Q1",
                "current_quarter": "2024Q1",
            }
        }
    )
