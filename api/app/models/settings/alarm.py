"""Alarm / reminder model and CRUD schemas (Settings domain).

Alarms here are strictly recurring financial events. There are two recurrence
types:

* `Y` — yearly. `alarm_date` holds the recurring anchor as `MMDD` (4 chars).
* `M` — monthly. `alarm_date` holds the recurring anchor as `DD` (2 chars).

One-off reminders are out of scope and would belong to a calendar integration.
"""
from __future__ import annotations

from typing import Literal

from pydantic import ConfigDict, field_validator
from sqlmodel import Field, SQLModel

AlarmType = Literal["Y", "M"]


_ALARM_EXAMPLE = {
    "alarm_id": 1,
    "alarm_type": "Y",
    "alarm_date": "0531",
    "content": "報稅",
    "due_date": None,
}


def _validate_alarm_date(value: str, alarm_type: AlarmType | None) -> str:
    if alarm_type is None:
        # On partial-update (AlarmUpdate) we may receive alarm_date without
        # alarm_type. Skip the type-specific check; the row's existing
        # alarm_type still governs interpretation.
        return value
    if alarm_type == "Y":
        if len(value) != 4 or not value.isdigit():
            raise ValueError("alarm_date must be 4-digit MMDD for alarm_type=Y")
        mm = int(value[:2])
        dd = int(value[2:])
        if not (1 <= mm <= 12 and 1 <= dd <= 31):
            raise ValueError(f"alarm_date {value} out of range (MM 01-12, DD 01-31)")
    else:  # M
        if len(value) != 2 or not value.isdigit():
            raise ValueError("alarm_date must be 2-digit DD for alarm_type=M")
        dd = int(value)
        if not (1 <= dd <= 31):
            raise ValueError(f"alarm_date {value} out of range (DD 01-31)")
    return value


class Alarm(SQLModel, table=True):
    __tablename__ = "Alarm"

    alarm_id: int | None = Field(
        default=None, primary_key=True, description="Autoincrement PK", schema_extra={"examples": [1]}
    )
    # Stored as plain str on the table (SQLModel can't translate Literal to a
    # SQL column type). The Create/Update/Read schemas below enforce Y/M.
    alarm_type: str = Field(
        ...,
        description="Recurrence: 'Y' yearly, 'M' monthly",
        schema_extra={"examples": ["Y"]},
    )
    alarm_date: str = Field(
        ...,
        description="Recurring anchor: MMDD for Y, DD for M",
        schema_extra={"examples": ["0531"]},
    )
    content: str = Field(..., description="Free-form reminder text", schema_extra={"examples": ["報稅"]})
    due_date: str | None = Field(
        default=None,
        description="Optional YYYYMM cutoff: stop expanding occurrences past this month",
        schema_extra={"examples": ["202612"]},
    )

    model_config = ConfigDict(json_schema_extra={"example": _ALARM_EXAMPLE})


class AlarmCreate(SQLModel):
    alarm_type: AlarmType = Field(
        ...,
        description="Recurrence: 'Y' yearly, 'M' monthly",
        schema_extra={"examples": ["Y"]},
    )
    alarm_date: str = Field(
        ...,
        description="Recurring anchor: MMDD for Y, DD for M",
        schema_extra={"examples": ["0531"]},
    )
    content: str = Field(..., description="Reminder text", schema_extra={"examples": ["報稅"]})
    due_date: str | None = Field(default=None, description="Optional YYYYMM cutoff", schema_extra={"examples": ["202612"]})

    model_config = ConfigDict(json_schema_extra={"example": {k: v for k, v in _ALARM_EXAMPLE.items() if k != "alarm_id"}})

    @field_validator("alarm_date")
    @classmethod
    def _check_date(cls, v: str, info):
        return _validate_alarm_date(v, info.data.get("alarm_type"))


class AlarmUpdate(SQLModel):
    alarm_type: AlarmType | None = Field(
        default=None,
        description="Recurrence: 'Y' yearly, 'M' monthly",
        schema_extra={"examples": ["Y"]},
    )
    alarm_date: str | None = Field(
        default=None,
        description="Recurring anchor: MMDD for Y, DD for M",
        schema_extra={"examples": ["0531"]},
    )
    content: str | None = Field(default=None, description="Reminder text", schema_extra={"examples": ["報稅"]})
    due_date: str | None = Field(default=None, description="Optional YYYYMM cutoff", schema_extra={"examples": ["202612"]})

    model_config = ConfigDict(json_schema_extra={"example": {"content": "報稅"}})

    @field_validator("alarm_date")
    @classmethod
    def _check_date(cls, v: str | None, info):
        if v is None:
            return v
        return _validate_alarm_date(v, info.data.get("alarm_type"))


class AlarmRead(SQLModel):
    alarm_id: int = Field(..., description="Autoincrement PK", schema_extra={"examples": [1]})
    alarm_type: AlarmType = Field(
        ...,
        description="Recurrence: 'Y' yearly, 'M' monthly",
        schema_extra={"examples": ["Y"]},
    )
    alarm_date: str = Field(
        ...,
        description="Recurring anchor: MMDD for Y, DD for M",
        schema_extra={"examples": ["0531"]},
    )
    content: str = Field(..., description="Reminder text", schema_extra={"examples": ["報稅"]})
    due_date: str | None = Field(default=None, description="Optional YYYYMM cutoff", schema_extra={"examples": ["202612"]})

    model_config = ConfigDict(json_schema_extra={"example": _ALARM_EXAMPLE})
