"""Stock asset models: StockJournal (holding record) + StockDetail (transaction).

Note: the legacy misspellings `excute_*` (instead of `execute_*`) are
preserved verbatim — BE-005 data migration depends on matching column names.
"""
from __future__ import annotations

from typing import Literal

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

StockExcuteType = Literal["buy", "sell", "stock", "cash"]


_STOCK_JOURNAL_EXAMPLE = {
    "stock_id": "STK-H-001",
    "stock_code": "AAPL",
    "stock_name": "Apple Inc.",
    "asset_id": "AC-STK-001",
    "expected_spend": 10000.0,
    "category_id": "SC-001",
}
_STOCK_DETAIL_EXAMPLE = {
    "distinct_number": 1,
    "stock_id": "STK-H-001",
    "excute_type": "buy",
    "excute_amount": 10.0,
    "excute_price": 180.50,
    "excute_date": "20260418",
    "account_id": "BANK-CHASE-01",
    "account_name": "Chase Checking",
    "memo": "Initial buy",
}


class StockJournal(SQLModel, table=True):
    __tablename__ = "Stock_Journal"

    stock_id: str = Field(..., primary_key=True, description="Holding business ID", schema_extra={"examples": ["STK-H-001"]})
    stock_code: str = Field(..., description="Ticker symbol", schema_extra={"examples": ["AAPL"]})
    stock_name: str = Field(..., description="Stock display name", schema_extra={"examples": ["Apple Inc."]})
    asset_id: str = Field(..., description="Asset category ID", schema_extra={"examples": ["AC-STK-001"]})
    expected_spend: float = Field(..., description="Planned investment amount for this holding entry (one-shot purchase budget; not a recurring premium — see Insurance.expected_spend for that)", schema_extra={"examples": [10000.0]})
    category_id: str | None = Field(default=None, description="Allocation category id (references Stock_Category.category_id); null = unclassified", schema_extra={"examples": ["SC-001"]})

    model_config = ConfigDict(json_schema_extra={"example": _STOCK_JOURNAL_EXAMPLE})


class StockJournalCreate(SQLModel):
    stock_id: str = Field(..., description="Holding business ID", schema_extra={"examples": ["STK-H-001"]})
    stock_code: str = Field(..., description="Ticker symbol", schema_extra={"examples": ["AAPL"]})
    stock_name: str = Field(..., description="Stock display name", schema_extra={"examples": ["Apple Inc."]})
    asset_id: str = Field(..., description="Asset category ID", schema_extra={"examples": ["AC-STK-001"]})
    expected_spend: float = Field(..., description="Planned investment amount for this holding entry (one-shot purchase budget; not a recurring premium — see Insurance.expected_spend for that)", schema_extra={"examples": [10000.0]})
    category_id: str | None = Field(default=None, description="Allocation category id (references Stock_Category.category_id); optional at creation", schema_extra={"examples": ["SC-001"]})

    model_config = ConfigDict(json_schema_extra={"example": _STOCK_JOURNAL_EXAMPLE})


class StockJournalUpdate(SQLModel):
    stock_code: str | None = Field(default=None, description="Ticker symbol", schema_extra={"examples": ["AAPL"]})
    stock_name: str | None = Field(default=None, description="Stock display name", schema_extra={"examples": ["Apple Inc."]})
    asset_id: str | None = Field(default=None, description="Asset category ID", schema_extra={"examples": ["AC-STK-001"]})
    expected_spend: float | None = Field(default=None, description="Planned investment amount for this holding entry (one-shot purchase budget; not a recurring premium — see Insurance.expected_spend for that)", schema_extra={"examples": [12000.0]})
    category_id: str | None = Field(default=None, description="Allocation category id (references Stock_Category.category_id)", schema_extra={"examples": ["SC-002"]})

    model_config = ConfigDict(json_schema_extra={"example": {"expected_spend": 12000.0}})


class StockJournalRead(SQLModel):
    stock_id: str = Field(..., description="Holding business ID", schema_extra={"examples": ["STK-H-001"]})
    stock_code: str = Field(..., description="Ticker symbol", schema_extra={"examples": ["AAPL"]})
    stock_name: str = Field(..., description="Stock display name", schema_extra={"examples": ["Apple Inc."]})
    asset_id: str = Field(..., description="Asset category ID", schema_extra={"examples": ["AC-STK-001"]})
    expected_spend: float = Field(..., description="Planned investment amount for this holding entry (one-shot purchase budget; not a recurring premium — see Insurance.expected_spend for that)", schema_extra={"examples": [10000.0]})
    category_id: str | None = Field(default=None, description="Allocation category id (references Stock_Category.category_id); null = unclassified", schema_extra={"examples": ["SC-001"]})

    model_config = ConfigDict(json_schema_extra={"example": _STOCK_JOURNAL_EXAMPLE})


class StockDetail(SQLModel, table=True):
    __tablename__ = "Stock_Detail"

    distinct_number: int | None = Field(default=None, primary_key=True, description="Autoincrement PK", schema_extra={"examples": [1]})
    stock_id: str = Field(..., description="FK reference to Stock_Journal.stock_id", schema_extra={"examples": ["STK-H-001"]})
    excute_type: str = Field(..., description="buy / sell / dividend", schema_extra={"examples": ["buy"]})
    excute_amount: float = Field(..., description="Quantity traded", schema_extra={"examples": [10.0]})
    excute_price: float = Field(..., description="Price per share", schema_extra={"examples": [180.50]})
    excute_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20260418"]})
    account_id: str = Field(..., description="Settling account business ID", schema_extra={"examples": ["BANK-CHASE-01"]})
    account_name: str = Field(..., description="Settling account display name", schema_extra={"examples": ["Chase Checking"]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["Initial buy"]})

    model_config = ConfigDict(json_schema_extra={"example": _STOCK_DETAIL_EXAMPLE})


class StockDetailCreate(SQLModel):
    stock_id: str = Field(..., description="FK to Stock_Journal.stock_id", schema_extra={"examples": ["STK-H-001"]})
    excute_type: StockExcuteType = Field(..., description="Transaction type: buy/sell/stock/cash", schema_extra={"examples": ["buy"]})
    excute_amount: float = Field(..., description="Quantity traded", schema_extra={"examples": [10.0]})
    excute_price: float = Field(..., description="Price per share", schema_extra={"examples": [180.50]})
    excute_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20260418"]})
    account_id: str = Field(..., description="Settling account business ID", schema_extra={"examples": ["BANK-CHASE-01"]})
    account_name: str = Field(..., description="Settling account display name", schema_extra={"examples": ["Chase Checking"]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["Initial buy"]})

    model_config = ConfigDict(
        json_schema_extra={"example": {k: v for k, v in _STOCK_DETAIL_EXAMPLE.items() if k != "distinct_number"}}
    )


class StockDetailUpdate(SQLModel):
    excute_type: StockExcuteType | None = Field(default=None, description="Transaction type", schema_extra={"examples": ["sell"]})
    excute_amount: float | None = Field(default=None, description="Quantity traded", schema_extra={"examples": [5.0]})
    excute_price: float | None = Field(default=None, description="Price per share", schema_extra={"examples": [185.0]})
    excute_date: str | None = Field(default=None, description="YYYYMMDD", schema_extra={"examples": ["20260420"]})
    account_id: str | None = Field(default=None, description="Settling account business ID", schema_extra={"examples": ["BANK-CHASE-01"]})
    account_name: str | None = Field(default=None, description="Settling account display name", schema_extra={"examples": ["Chase Checking"]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["Updated"]})

    model_config = ConfigDict(json_schema_extra={"example": {"memo": "Updated"}})


class StockDetailRead(SQLModel):
    distinct_number: int = Field(..., description="Autoincrement PK", schema_extra={"examples": [1]})
    stock_id: str = Field(..., description="FK to Stock_Journal.stock_id", schema_extra={"examples": ["STK-H-001"]})
    excute_type: str = Field(..., description="buy / sell / dividend", schema_extra={"examples": ["buy"]})
    excute_amount: float = Field(..., description="Quantity traded", schema_extra={"examples": [10.0]})
    excute_price: float = Field(..., description="Price per share", schema_extra={"examples": [180.50]})
    excute_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20260418"]})
    account_id: str = Field(..., description="Settling account business ID", schema_extra={"examples": ["BANK-CHASE-01"]})
    account_name: str = Field(..., description="Settling account display name", schema_extra={"examples": ["Chase Checking"]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["Initial buy"]})

    model_config = ConfigDict(json_schema_extra={"example": _STOCK_DETAIL_EXAMPLE})


_STOCK_PNL_SUMMARY_EXAMPLE = {
    "stock_id": "STK-H-001",
    "stock_code": "AAPL",
    "stock_name": "Apple Inc.",
    "shares": 90.0,
    "cost": 14850.0,
    "market_value": 16200.0,
    "realized": 1500.0,
    "dividends_total": 450.0,
    "unrealized": 1350.0,
    "unrealized_pct": 0.0909,
    "cash_yield": 0.0278,
    "cost_yield": 0.0303,
    "fx_code": "USD",
    "close_price": 180.0,
    "price_date": "20260430",
}


class StockPnlSummaryRead(SQLModel):
    """Computed per-holding performance, derived fresh from ``Stock_Detail``.

    All money fields are in the holding's own ``fx_code`` (no base-currency
    conversion). Cost uses moving-average basis; ``realized`` is the signed sum
    of per-sale price-vs-average-cost gains (capital gains only — dividends are
    in ``dividends_total``). ``unrealized``/``market_value`` are ``None`` when no
    price snapshot exists for the ticker; the percent/yield fields are fractions
    (0.05 = 5%) and ``None`` when their denominator is zero.
    """

    stock_id: str = Field(..., description="Holding business ID", schema_extra={"examples": ["STK-H-001"]})
    stock_code: str = Field(..., description="Ticker symbol", schema_extra={"examples": ["AAPL"]})
    stock_name: str = Field(..., description="Stock display name", schema_extra={"examples": ["Apple Inc."]})
    shares: float = Field(..., description="Net shares currently held", schema_extra={"examples": [90.0]})
    cost: float = Field(..., description="Moving-average cost basis of held shares (own currency)", schema_extra={"examples": [14850.0]})
    market_value: float | None = Field(default=None, description="shares × latest close price; null when no price snapshot exists", schema_extra={"examples": [16200.0]})
    realized: float = Field(..., description="Signed realized capital gain/loss from sells (own currency); dividends excluded", schema_extra={"examples": [1500.0]})
    dividends_total: float = Field(..., description="Cumulative cash dividends received (own currency)", schema_extra={"examples": [450.0]})
    unrealized: float | None = Field(default=None, description="market_value − cost; null when no price snapshot exists", schema_extra={"examples": [1350.0]})
    unrealized_pct: float | None = Field(default=None, description="unrealized ÷ cost as a fraction; null when cost is 0 or no price", schema_extra={"examples": [0.0909]})
    cash_yield: float | None = Field(default=None, description="Trailing-12-month cash dividends ÷ market_value (fraction); null when market_value is 0/None", schema_extra={"examples": [0.0278]})
    cost_yield: float | None = Field(default=None, description="Cumulative cash dividends ÷ cost (fraction); null when cost is 0", schema_extra={"examples": [0.0303]})
    fx_code: str = Field(..., description="Currency the figures are expressed in", schema_extra={"examples": ["USD"]})
    close_price: float | None = Field(default=None, description="Latest close price used for market_value; null when none exists", schema_extra={"examples": [180.0]})
    price_date: str | None = Field(default=None, description="YYYYMMDD of the close price used; null when none exists", schema_extra={"examples": ["20260430"]})

    model_config = ConfigDict(json_schema_extra={"example": _STOCK_PNL_SUMMARY_EXAMPLE})
