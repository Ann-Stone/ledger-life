"""CodeData model and CRUD schemas (Settings domain)."""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


_CODE_EXAMPLE = {
    "code_id": "E01",
    "code_type": "Floating",
    "name": "Food",
    "parent_id": None,
    "in_use": "Y",
    "code_index": 1,
    "is_annual_event": False,
}


class CodeData(SQLModel, table=True):
    __tablename__ = "Code_Data"

    code_id: str = Field(
        ..., primary_key=True, description="Business identifier", schema_extra={"examples": ["E01"]}
    )
    code_type: str = Field(
        ...,
        description="Code category: Fixed / Floating / Invest / Income / Transfer / etc.",
        schema_extra={"examples": ["Floating"]},
    )
    name: str = Field(..., description="Display name", schema_extra={"examples": ["Food"]})
    parent_id: str | None = Field(
        default=None,
        description="Parent code_id; null for main codes, set to parent's code_id for sub-codes",
        schema_extra={"examples": [None]},
    )
    in_use: str = Field(..., description="Active flag (Y/N)", schema_extra={"examples": ["Y"]})
    code_index: int = Field(..., description="Dropdown order, ORDER BY ASC", schema_extra={"examples": [1]})
    is_annual_event: bool = Field(
        default=False,
        description="Budget as a single annual envelope instead of 12 monthly amounts",
        schema_extra={"examples": [False]},
    )

    model_config = ConfigDict(json_schema_extra={"example": _CODE_EXAMPLE})


class CodeDataCreate(SQLModel):
    code_id: str = Field(..., description="Business identifier", schema_extra={"examples": ["E01"]})
    code_type: str = Field(
        ...,
        description="Code category: Fixed / Floating / Invest / Income / Transfer / etc.",
        schema_extra={"examples": ["Floating"]},
    )
    name: str = Field(..., description="Display name", schema_extra={"examples": ["Food"]})
    parent_id: str | None = Field(
        default=None, description="Parent code_id; null for main codes", schema_extra={"examples": [None]}
    )
    in_use: str = Field(default="Y", description="Active flag", schema_extra={"examples": ["Y"]})
    code_index: int | None = Field(
        default=None,
        description="Dropdown order; auto-filled with max+1 when omitted",
        schema_extra={"examples": [1]},
    )
    is_annual_event: bool = Field(
        default=False, description="Budget as a single annual envelope", schema_extra={"examples": [False]}
    )

    model_config = ConfigDict(json_schema_extra={"example": _CODE_EXAMPLE})


class CodeDataUpdate(SQLModel):
    code_type: str | None = Field(default=None, description="code type", schema_extra={"examples": ["Fixed"]})
    name: str | None = Field(default=None, description="Display name", schema_extra={"examples": ["Renamed"]})
    parent_id: str | None = Field(default=None, description="Parent code_id", schema_extra={"examples": [None]})
    in_use: str | None = Field(default=None, description="Active flag", schema_extra={"examples": ["N"]})
    code_index: int | None = Field(default=None, description="Dropdown order", schema_extra={"examples": [2]})
    is_annual_event: bool | None = Field(
        default=None, description="Budget as a single annual envelope", schema_extra={"examples": [True]}
    )

    model_config = ConfigDict(json_schema_extra={"example": {"in_use": "N"}})


class CodeDataRead(SQLModel):
    code_id: str = Field(..., description="Business identifier", schema_extra={"examples": ["E01"]})
    code_type: str = Field(..., description="code type", schema_extra={"examples": ["Floating"]})
    name: str = Field(..., description="Display name", schema_extra={"examples": ["Food"]})
    parent_id: str | None = Field(default=None, description="Parent code_id", schema_extra={"examples": [None]})
    in_use: str = Field(..., description="Active flag", schema_extra={"examples": ["Y"]})
    code_index: int = Field(..., description="Dropdown order", schema_extra={"examples": [1]})
    is_annual_event: bool = Field(
        default=False, description="Budget as a single annual envelope", schema_extra={"examples": [False]}
    )

    model_config = ConfigDict(json_schema_extra={"example": _CODE_EXAMPLE})


class CodeWithSubs(CodeDataRead):
    sub_codes: list[CodeDataRead] = Field(
        default_factory=list,
        description="Nested sub-codes",
        schema_extra={"examples": [[]]},
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {**_CODE_EXAMPLE, "sub_codes": []}}
    )
