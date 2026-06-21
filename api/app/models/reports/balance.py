"""Balance sheet response schemas (Reports domain)."""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class BalanceLine(SQLModel):
    name: str = Field(..., description="Entity name", schema_extra={"examples": ["Cathay Bank"]})
    amount: float = Field(..., description="Amount in base currency", schema_extra={"examples": [123456.78]})
    original_amount: float = Field(
        ...,
        description="Amount in original currency (pre-FX); equals amount for base-currency entities",
        schema_extra={"examples": [4000.0]},
    )
    currency: str = Field(..., description="Original currency", schema_extra={"examples": ["TWD"]})

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"name": "Cathay Bank", "amount": 123456.78, "original_amount": 123456.78, "currency": "TWD"}
        }
    )


class BalanceAssets(SQLModel):
    accounts: list[BalanceLine] = Field(default_factory=list, description="Cash account balances", schema_extra={"examples": [[]]})
    stocks: list[BalanceLine] = Field(default_factory=list, description="Stock holdings (market value)", schema_extra={"examples": [[]]})
    estates: list[BalanceLine] = Field(default_factory=list, description="Real estate market value", schema_extra={"examples": [[]]})
    insurances: list[BalanceLine] = Field(default_factory=list, description="Insurance surrender value", schema_extra={"examples": [[]]})

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "accounts": [{"name": "Cathay Bank", "amount": 123456.78, "original_amount": 123456.78, "currency": "TWD"}],
                "stocks": [],
                "estates": [],
                "insurances": [],
            }
        }
    )


class BalanceLiabilities(SQLModel):
    loans: list[BalanceLine] = Field(default_factory=list, description="Outstanding loan balances", schema_extra={"examples": [[]]})
    credit_cards: list[BalanceLine] = Field(default_factory=list, description="Credit card outstanding balances", schema_extra={"examples": [[]]})

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "loans": [{"name": "Mortgage", "amount": -250000.0, "original_amount": -250000.0, "currency": "TWD"}],
                "credit_cards": [],
            }
        }
    )


class BalanceSheetRead(SQLModel):
    assets: BalanceAssets = Field(..., description="Asset breakdown")
    liabilities: BalanceLiabilities = Field(..., description="Liability breakdown")
    net_worth: float = Field(
        ...,
        description="Total assets minus total liabilities in base currency",
        schema_extra={"examples": [987654.32]},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "assets": {
                    "accounts": [{"name": "Cathay Bank", "amount": 123456.78, "original_amount": 123456.78, "currency": "TWD"}],
                    "stocks": [],
                    "estates": [],
                    "insurances": [],
                },
                "liabilities": {
                    "loans": [{"name": "Mortgage", "amount": -250000.0, "original_amount": -250000.0, "currency": "TWD"}],
                    "credit_cards": [],
                },
                "net_worth": 987654.32,
            }
        }
    )
