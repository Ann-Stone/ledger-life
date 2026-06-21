"""Alarm response schema for dashboard view (BE-028)."""
from __future__ import annotations

from typing import Literal

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class AlarmItem(SQLModel):
    date: str = Field(
        ...,
        description="Expanded occurrence date in YYYYMMDD",
        schema_extra={"examples": ["20260531"]},
    )
    content: str = Field(
        ..., description="Alarm content", schema_extra={"examples": ["報稅"]}
    )
    alarm_type: Literal["Y", "M"] = Field(
        ...,
        description="Recurrence type: 'Y' yearly, 'M' monthly",
        schema_extra={"examples": ["Y"]},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"date": "20260531", "content": "報稅", "alarm_type": "Y"}
        }
    )
