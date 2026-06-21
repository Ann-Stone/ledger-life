"""Account model and CRUD schemas (Settings domain)."""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


_ACCOUNT_EXAMPLE = {
    "id": 1,
    "account_id": "BANK-CHASE-01",
    "name": "Chase Checking",
    "account_type": "bank",
    "fx_code": "USD",
    "is_calculate": "Y",
    "in_use": "Y",
    "discount": 1.0,
    "memo": "Primary checking",
    "owner": "stone",
    "account_index": 1,
}
_ACCOUNT_CREATE_EXAMPLE = {k: v for k, v in _ACCOUNT_EXAMPLE.items() if k != "id"}


class Account(SQLModel, table=True):
    __tablename__ = "Account"

    id: int | None = Field(
        default=None,
        primary_key=True,
        description="Internal autoincrement PK used by FKs",
        schema_extra={"examples": [1]},
    )
    account_id: str = Field(
        ...,
        max_length=20,
        unique=True,
        index=True,
        description="User-supplied business identifier",
        schema_extra={"examples": ["BANK-CHASE-01"]},
    )
    name: str = Field(
        ..., description="Human-readable account name", schema_extra={"examples": ["Chase Checking"]}
    )
    account_type: str = Field(
        ..., description="Account type (bank / cash / broker / ...)", schema_extra={"examples": ["bank"]}
    )
    fx_code: str = Field(
        ..., description="Currency code (USD, TWD, JPY, ...)", schema_extra={"examples": ["USD"]}
    )
    is_calculate: str = Field(
        ..., description="Include this account in totals (Y/N)", schema_extra={"examples": ["Y"]}
    )
    in_use: str = Field(..., description="Active flag (Y/N)", schema_extra={"examples": ["Y"]})
    discount: float = Field(
        ..., description="Discount multiplier applied to balance (1.0 = no discount)", schema_extra={"examples": [1.0]}
    )
    memo: str | None = Field(
        default=None, description="Free-form memo", schema_extra={"examples": ["Primary checking"]}
    )
    owner: str | None = Field(default=None, description="Owner label", schema_extra={"examples": ["stone"]})
    account_index: int = Field(
        ..., description="Dropdown order, ORDER BY ASC", schema_extra={"examples": [1]}
    )

    model_config = ConfigDict(json_schema_extra={"example": _ACCOUNT_EXAMPLE})


class AccountCreate(SQLModel):
    account_id: str = Field(
        ..., max_length=20, description="User-supplied business identifier",
        schema_extra={"examples": ["BANK-CHASE-01"]},
    )
    name: str = Field(..., description="Account name", schema_extra={"examples": ["Chase Checking"]})
    account_type: str = Field(..., description="Account type", schema_extra={"examples": ["bank"]})
    fx_code: str = Field(..., description="Currency code", schema_extra={"examples": ["USD"]})
    is_calculate: str = Field(default="Y", description="Include in totals (Y/N)", schema_extra={"examples": ["Y"]})
    in_use: str = Field(default="Y", description="Active flag (Y/N)", schema_extra={"examples": ["Y"]})
    discount: float = Field(default=1.0, description="Discount multiplier", schema_extra={"examples": [1.0]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["Primary checking"]})
    owner: str | None = Field(default=None, description="Owner label", schema_extra={"examples": ["stone"]})
    account_index: int | None = Field(
        default=None,
        description="Optional sort order; auto-filled with max(account_index)+1 when omitted",
        schema_extra={"examples": [10]},
    )

    model_config = ConfigDict(json_schema_extra={"example": _ACCOUNT_CREATE_EXAMPLE})


class AccountUpdate(SQLModel):
    account_id: str | None = Field(default=None, max_length=20, description="Business identifier", schema_extra={"examples": ["BANK-CHASE-01"]})
    name: str | None = Field(default=None, description="Account name", schema_extra={"examples": ["Chase Checking"]})
    account_type: str | None = Field(default=None, description="Account type", schema_extra={"examples": ["bank"]})
    fx_code: str | None = Field(default=None, description="Currency code", schema_extra={"examples": ["USD"]})
    is_calculate: str | None = Field(default=None, description="Include in totals (Y/N)", schema_extra={"examples": ["Y"]})
    in_use: str | None = Field(default=None, description="Active flag (Y/N)", schema_extra={"examples": ["N"]})
    discount: float | None = Field(default=None, description="Discount multiplier", schema_extra={"examples": [1.0]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["Primary checking"]})
    owner: str | None = Field(default=None, description="Owner label", schema_extra={"examples": ["stone"]})
    account_index: int | None = Field(default=None, description="Dropdown order", schema_extra={"examples": [1]})

    model_config = ConfigDict(json_schema_extra={"example": {"name": "Chase Checking Renamed", "in_use": "N"}})


class AccountRead(SQLModel):
    id: int = Field(..., description="Autoincrement PK", schema_extra={"examples": [1]})
    account_id: str = Field(..., description="Business identifier", schema_extra={"examples": ["BANK-CHASE-01"]})
    name: str = Field(..., description="Account name", schema_extra={"examples": ["Chase Checking"]})
    account_type: str = Field(..., description="Account type", schema_extra={"examples": ["bank"]})
    fx_code: str = Field(..., description="Currency code", schema_extra={"examples": ["USD"]})
    is_calculate: str = Field(..., description="Include in totals (Y/N)", schema_extra={"examples": ["Y"]})
    in_use: str = Field(..., description="Active flag (Y/N)", schema_extra={"examples": ["Y"]})
    discount: float = Field(..., description="Discount multiplier", schema_extra={"examples": [1.0]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["Primary checking"]})
    owner: str | None = Field(default=None, description="Owner label", schema_extra={"examples": ["stone"]})
    account_index: int = Field(..., description="Dropdown order", schema_extra={"examples": [1]})

    model_config = ConfigDict(json_schema_extra={"example": _ACCOUNT_EXAMPLE})
