"""Stock allocation response schemas (Reports domain).

A sub-breakdown of the ``stocks`` bucket from the asset composition view, split
by ``Stock_Journal.category_id``. Holdings whose category is null or points at a
deleted category fall into the synthetic "unclassified" share (``category_id``
is ``None``).
"""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class StockAllocationShare(SQLModel):
    category_id: str | None = Field(
        default=None,
        description="Stock_Category.category_id; null for the unclassified bucket",
        schema_extra={"examples": ["SC-001"]},
    )
    category_name: str = Field(
        ..., description="Category display name; '未分類' for the unclassified bucket", schema_extra={"examples": ["成長型"]}
    )
    amount: float = Field(
        ..., description="Latest-month stock value in base currency", schema_extra={"examples": [200000.0]}
    )
    share: float = Field(
        ..., description="Percentage of total stock value 0-100", schema_extra={"examples": [55.0]}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"category_id": "SC-001", "category_name": "成長型", "amount": 200000.0, "share": 55.0}
        }
    )


class StockAllocationRead(SQLModel):
    total: float = Field(
        ..., description="Total stock value in base currency", schema_extra={"examples": [363636.36]}
    )
    items: list[StockAllocationShare] = Field(
        ..., description="Per-category share, sums to 100% within rounding", schema_extra={"examples": [[]]}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 363636.36,
                "items": [
                    {"category_id": "SC-001", "category_name": "成長型", "amount": 200000.0, "share": 55.0},
                    {"category_id": "SC-002", "category_name": "債券", "amount": 100000.0, "share": 27.5},
                    {"category_id": None, "category_name": "未分類", "amount": 63636.36, "share": 17.5},
                ],
            }
        }
    )
