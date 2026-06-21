"""StockCategory model + CRUD schemas (Assets domain).

A user-maintained dictionary of stock allocation classes (e.g. growth / bond /
cash-equivalent). ``Stock_Journal.category_id`` references a row here; holdings
with a null/dangling reference are treated as "unclassified" in reports.

Categories are retired via ``in_use = "N"`` (soft-disable) rather than deleted
while still referenced, so existing holdings keep their classification.
"""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


_EXAMPLE = {
    "category_id": "SC-001",
    "name": "成長型",
    "in_use": "Y",
    "category_index": 1,
}


class StockCategory(SQLModel, table=True):
    __tablename__ = "Stock_Category"

    category_id: str = Field(..., primary_key=True, description="Category business ID", schema_extra={"examples": ["SC-001"]})
    name: str = Field(..., description="Display name", schema_extra={"examples": ["成長型"]})
    in_use: str = Field(default="Y", description="Active flag (Y/N)", schema_extra={"examples": ["Y"]})
    category_index: int = Field(..., description="Dropdown order, ORDER BY ASC", schema_extra={"examples": [1]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class StockCategoryCreate(SQLModel):
    name: str = Field(..., description="Display name", schema_extra={"examples": ["成長型"]})
    in_use: str = Field(default="Y", description="Active flag (Y/N)", schema_extra={"examples": ["Y"]})
    category_index: int | None = Field(default=None, description="Display order; server assigns max+1 when omitted", schema_extra={"examples": [1]})

    model_config = ConfigDict(json_schema_extra={"example": {"name": "成長型"}})


class StockCategoryUpdate(SQLModel):
    name: str | None = Field(default=None, description="Display name", schema_extra={"examples": ["成長股"]})
    in_use: str | None = Field(default=None, description="Active flag (Y/N); set 'N' to retire a category", schema_extra={"examples": ["N"]})
    category_index: int | None = Field(default=None, description="Dropdown order", schema_extra={"examples": [2]})

    model_config = ConfigDict(json_schema_extra={"example": {"in_use": "N"}})


class StockCategoryRead(SQLModel):
    category_id: str = Field(..., description="Category business ID", schema_extra={"examples": ["SC-001"]})
    name: str = Field(..., description="Display name", schema_extra={"examples": ["成長型"]})
    in_use: str = Field(..., description="Active flag (Y/N)", schema_extra={"examples": ["Y"]})
    category_index: int = Field(..., description="Dropdown order", schema_extra={"examples": [1]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})
