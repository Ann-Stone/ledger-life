"""CreditCard model and CRUD schemas (Settings domain).

Note: the legacy `carrier_no` column is intentionally dropped — see
README Decision Log.
"""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


_CREDIT_CARD_EXAMPLE = {
    "credit_card_id": "CC-VISA-01",
    "card_name": "Chase Sapphire",
    "card_no": "4111-XXXX-XXXX-1111",
    "last_day": 25,
    "charge_day": 15,
    "limit_date": 20,
    "card_expiry": "2026/08",
    "feedback_way": "cashback",
    "fx_code": "USD",
    "in_use": "Y",
    "credit_card_index": 1,
    "note": "Primary card",
}


class CreditCard(SQLModel, table=True):
    __tablename__ = "Credit_Card"

    credit_card_id: str = Field(
        ..., primary_key=True, description="Business identifier", schema_extra={"examples": ["CC-VISA-01"]}
    )
    card_name: str = Field(..., description="Display name", schema_extra={"examples": ["Chase Sapphire"]})
    card_no: str | None = Field(default=None, description="Card number", schema_extra={"examples": ["4111-XXXX-XXXX-1111"]})
    last_day: int | None = Field(default=None, description="Statement cut-off day of month", schema_extra={"examples": [25]})
    charge_day: int | None = Field(default=None, description="Charge day of month", schema_extra={"examples": [15]})
    limit_date: int | None = Field(default=None, description="Payment due day of month", schema_extra={"examples": [20]})
    card_expiry: str | None = Field(
        default=None,
        max_length=7,
        description="Card expiration year/month, free-form 'YYYY/MM'",
        schema_extra={"examples": ["2026/08"]},
    )
    feedback_way: str | None = Field(default=None, description="Rewards method", schema_extra={"examples": ["cashback"]})
    fx_code: str = Field(..., description="Billing currency code", schema_extra={"examples": ["USD"]})
    in_use: str = Field(..., description="Active flag (Y/N)", schema_extra={"examples": ["Y"]})
    credit_card_index: int = Field(..., description="Dropdown order, ORDER BY ASC", schema_extra={"examples": [1]})
    note: str | None = Field(default=None, description="Free-form note", schema_extra={"examples": ["Primary card"]})

    model_config = ConfigDict(json_schema_extra={"example": _CREDIT_CARD_EXAMPLE})


class CreditCardCreate(SQLModel):
    credit_card_id: str = Field(..., description="Business identifier", schema_extra={"examples": ["CC-VISA-01"]})
    card_name: str = Field(..., description="Display name", schema_extra={"examples": ["Chase Sapphire"]})
    card_no: str | None = Field(default=None, description="Card number", schema_extra={"examples": ["4111-XXXX-XXXX-1111"]})
    last_day: int | None = Field(default=None, description="Statement cut-off day", schema_extra={"examples": [25]})
    charge_day: int | None = Field(default=None, description="Charge day", schema_extra={"examples": [15]})
    limit_date: int | None = Field(default=None, description="Payment due day", schema_extra={"examples": [20]})
    card_expiry: str | None = Field(default=None, max_length=7, description="Card expiration year/month 'YYYY/MM'", schema_extra={"examples": ["2026/08"]})
    feedback_way: str | None = Field(default=None, description="Rewards method", schema_extra={"examples": ["cashback"]})
    fx_code: str = Field(..., description="Billing currency code", schema_extra={"examples": ["USD"]})
    in_use: str = Field(default="Y", description="Active flag", schema_extra={"examples": ["Y"]})
    credit_card_index: int | None = Field(default=None, description="Sort order; auto-filled with max+1 when omitted", schema_extra={"examples": [1]})
    note: str | None = Field(default=None, description="Free-form note", schema_extra={"examples": ["Primary card"]})

    model_config = ConfigDict(json_schema_extra={"example": _CREDIT_CARD_EXAMPLE})


class CreditCardUpdate(SQLModel):
    card_name: str | None = Field(default=None, description="Display name", schema_extra={"examples": ["Chase Sapphire"]})
    card_no: str | None = Field(default=None, description="Card number", schema_extra={"examples": ["4111-XXXX-XXXX-1111"]})
    last_day: int | None = Field(default=None, description="Statement cut-off day", schema_extra={"examples": [25]})
    charge_day: int | None = Field(default=None, description="Charge day", schema_extra={"examples": [15]})
    limit_date: int | None = Field(default=None, description="Payment due day", schema_extra={"examples": [20]})
    card_expiry: str | None = Field(default=None, max_length=7, description="Card expiration year/month 'YYYY/MM'", schema_extra={"examples": ["2027/12"]})
    feedback_way: str | None = Field(default=None, description="Rewards method", schema_extra={"examples": ["cashback"]})
    fx_code: str | None = Field(default=None, description="Billing currency code", schema_extra={"examples": ["USD"]})
    in_use: str | None = Field(default=None, description="Active flag", schema_extra={"examples": ["N"]})
    credit_card_index: int | None = Field(default=None, description="Dropdown order", schema_extra={"examples": [2]})
    note: str | None = Field(default=None, description="Free-form note", schema_extra={"examples": ["Retired"]})

    model_config = ConfigDict(json_schema_extra={"example": {"in_use": "N"}})


class CreditCardRead(SQLModel):
    credit_card_id: str = Field(..., description="Business identifier", schema_extra={"examples": ["CC-VISA-01"]})
    card_name: str = Field(..., description="Display name", schema_extra={"examples": ["Chase Sapphire"]})
    card_no: str | None = Field(default=None, description="Card number", schema_extra={"examples": ["4111-XXXX-XXXX-1111"]})
    last_day: int | None = Field(default=None, description="Statement cut-off day", schema_extra={"examples": [25]})
    charge_day: int | None = Field(default=None, description="Charge day", schema_extra={"examples": [15]})
    limit_date: int | None = Field(default=None, description="Payment due day", schema_extra={"examples": [20]})
    card_expiry: str | None = Field(default=None, max_length=7, description="Card expiration year/month 'YYYY/MM'", schema_extra={"examples": ["2026/08"]})
    feedback_way: str | None = Field(default=None, description="Rewards method", schema_extra={"examples": ["cashback"]})
    fx_code: str = Field(..., description="Billing currency code", schema_extra={"examples": ["USD"]})
    in_use: str = Field(..., description="Active flag", schema_extra={"examples": ["Y"]})
    credit_card_index: int = Field(..., description="Dropdown order", schema_extra={"examples": [1]})
    note: str | None = Field(default=None, description="Free-form note", schema_extra={"examples": ["Primary card"]})

    model_config = ConfigDict(json_schema_extra={"example": _CREDIT_CARD_EXAMPLE})
