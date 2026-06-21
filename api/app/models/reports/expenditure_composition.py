"""Expenditure composition (支出結構) response schemas — Reports domain.

A two-level tree of expense magnitude by category (action_main → Code_Data.name)
then subcategory (action_sub), each node carrying its share of the grand total
plus the category's fixed/variable type. Only Fixed + Floating rows are counted;
income, invest and transfer are excluded.
"""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

_SUB_EXAMPLE = {"code": "E0101", "name": "外食", "amount": 18000.0, "share": 12.5}


class ExpenditureSubNode(SQLModel):
    code: str = Field(
        ...,
        description="action_sub code_id ('' for the un-subcategorized remainder)",
        schema_extra={"examples": ["E0101"]},
    )
    name: str = Field(
        ..., description="Subcategory display name (Code_Data.name)", schema_extra={"examples": ["外食"]}
    )
    amount: float = Field(
        ..., description="Expense magnitude in base currency, positive", schema_extra={"examples": [18000.0]}
    )
    share: float = Field(
        ..., description="Percentage of grand total expense", schema_extra={"examples": [12.5]}
    )

    model_config = ConfigDict(json_schema_extra={"example": _SUB_EXAMPLE})


_CAT_EXAMPLE = {
    "code": "E01",
    "name": "餐飲",
    "type": "Floating",
    "amount": 42000.0,
    "share": 29.1,
    "children": [_SUB_EXAMPLE],
}


class ExpenditureCategoryNode(SQLModel):
    code: str = Field(..., description="action_main code_id", schema_extra={"examples": ["E01"]})
    name: str = Field(
        ..., description="Category display name (Code_Data.name)", schema_extra={"examples": ["餐飲"]}
    )
    type: str = Field(
        ..., description="action_main_type: Fixed or Floating", schema_extra={"examples": ["Floating"]}
    )
    amount: float = Field(
        ..., description="Expense magnitude in base currency, positive", schema_extra={"examples": [42000.0]}
    )
    share: float = Field(
        ..., description="Percentage of grand total expense", schema_extra={"examples": [29.1]}
    )
    children: list[ExpenditureSubNode] = Field(
        ...,
        description="Subcategory nodes, empty when the category has no sub-codes",
        schema_extra={"examples": [[_SUB_EXAMPLE]]},
    )

    model_config = ConfigDict(json_schema_extra={"example": _CAT_EXAMPLE})


_COMPOSITION_EXAMPLE = {
    "total": 144000.0,
    "fixed_total": 60000.0,
    "floating_total": 84000.0,
    "categories": [_CAT_EXAMPLE],
}


class ExpenditureCompositionRead(SQLModel):
    total: float = Field(
        ..., description="Grand total expense in base currency", schema_extra={"examples": [144000.0]}
    )
    fixed_total: float = Field(
        ..., description="Sum of Fixed-type categories", schema_extra={"examples": [60000.0]}
    )
    floating_total: float = Field(
        ..., description="Sum of Floating-type categories", schema_extra={"examples": [84000.0]}
    )
    categories: list[ExpenditureCategoryNode] = Field(
        ...,
        description="Category nodes, ordered by amount descending",
        schema_extra={"examples": [[_CAT_EXAMPLE]]},
    )

    model_config = ConfigDict(json_schema_extra={"example": _COMPOSITION_EXAMPLE})
