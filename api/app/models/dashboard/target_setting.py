"""TargetSetting model — annual target value tracker."""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


_EXAMPLE = {
    "distinct_number": "11",
    "target_year": "2026",
    "setting_value": "存頭期款 200 萬",
    "is_done": "N",
}


class TargetSetting(SQLModel, table=True):
    __tablename__ = "Target_Setting"

    distinct_number: str = Field(
        ...,
        primary_key=True,
        description="Sequential serial ID (stored as str, auto-assigned on create)",
        schema_extra={"examples": ["11"]},
    )
    target_year: str = Field(..., description="YYYY", schema_extra={"examples": ["2026"]})
    setting_value: str = Field(
        ...,
        max_length=45,
        description=(
            "Target description / value. Free-form text — typically the "
            "user's note about what the target is. May occasionally hold "
            "a number (parse in caller if needed)."
        ),
        schema_extra={"examples": ["存頭期款 200 萬"]},
    )
    is_done: str = Field(..., description="Y/N", schema_extra={"examples": ["N"]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class TargetSettingCreate(SQLModel):
    setting_value: str = Field(
        ...,
        max_length=45,
        description="Target description / value (free-form text)",
        schema_extra={"examples": ["存頭期款 200 萬"]},
    )
    target_year: str | None = Field(
        default=None,
        description="YYYY; defaults to the current year when omitted",
        schema_extra={"examples": ["2026"]},
    )
    is_done: str | None = Field(
        default=None,
        description="Y/N; defaults to N when omitted",
        schema_extra={"examples": ["N"]},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"setting_value": "存頭期款 200 萬"}
        }
    )


class TargetSettingUpdate(SQLModel):
    target_year: str | None = Field(default=None, description="YYYY", schema_extra={"examples": ["2026"]})
    setting_value: str | None = Field(default=None, max_length=45, description="Target description / value", schema_extra={"examples": ["Buy a house by Q4"]})
    is_done: str | None = Field(default=None, description="Y/N", schema_extra={"examples": ["Y"]})

    model_config = ConfigDict(json_schema_extra={"example": {"is_done": "Y"}})


class TargetSettingRead(SQLModel):
    distinct_number: str = Field(
        ...,
        description="Sequential serial ID",
        schema_extra={"examples": ["11"]},
    )
    target_year: str = Field(..., description="YYYY", schema_extra={"examples": ["2026"]})
    setting_value: str = Field(..., max_length=45, description="Target description / value", schema_extra={"examples": ["存頭期款 200 萬"]})
    is_done: str = Field(..., description="Y/N", schema_extra={"examples": ["N"]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})
