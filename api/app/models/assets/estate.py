"""Estate (real-estate) asset models: Estate + EstateJournal."""
from __future__ import annotations

from typing import Literal

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

EstateStatus = Literal["idle", "live", "rent", "sold"]
EstateExcuteType = Literal["tax", "fee", "insurance", "fix", "rent", "deposit"]


_ESTATE_EXAMPLE = {
    "estate_id": "EST-001",
    "estate_name": "Condo",
    "estate_type": "residential",
    "estate_address": "123 Main St",
    "asset_id": "AC-REAL-001",
    "obtain_date": "20200101",
    "loan_id": "LN-001",
    "estate_status": "live",
    "fx_code": "TWD",
    "region": "臺北市",
    "memo": "Primary residence",
}
_ESTATE_JOURNAL_EXAMPLE = {
    "distinct_number": 1,
    "estate_id": "EST-001",
    "estate_excute_type": "tax",
    "excute_price": 500000.0,
    "excute_date": "20200101",
    "memo": "Closing",
}


class Estate(SQLModel, table=True):
    __tablename__ = "Estate"

    estate_id: str = Field(..., primary_key=True, description="Estate business ID", schema_extra={"examples": ["EST-001"]})
    estate_name: str = Field(..., description="Estate display name", schema_extra={"examples": ["Condo"]})
    estate_type: str = Field(..., description="Estate type (residential / commercial / ...)", schema_extra={"examples": ["residential"]})
    estate_address: str = Field(..., description="Physical address", schema_extra={"examples": ["123 Main St"]})
    asset_id: str = Field(..., description="Asset category ID", schema_extra={"examples": ["AC-REAL-001"]})
    fx_code: str = Field(default="TWD", description="Currency code (TWD; USD/JPY/... for overseas property)", schema_extra={"examples": ["TWD"]})
    obtain_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20200101"]})
    loan_id: str | None = Field(default=None, description="Associated loan ID", schema_extra={"examples": ["LN-001"]})
    estate_status: str = Field(..., description="Status (idle / live / rent / sold)", schema_extra={"examples": ["live"]})
    region: str | None = Field(default=None, description="House-price-index 縣市 (全國/臺北市/新北市/桃園市/臺中市/臺南市/高雄市); null → 全國", schema_extra={"examples": ["臺北市"]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["Primary residence"]})

    model_config = ConfigDict(json_schema_extra={"example": _ESTATE_EXAMPLE})


class EstateCreate(SQLModel):
    estate_id: str = Field(..., description="Estate business ID", schema_extra={"examples": ["EST-001"]})
    estate_name: str = Field(..., description="Estate display name", schema_extra={"examples": ["Condo"]})
    estate_type: str = Field(..., description="Estate type", schema_extra={"examples": ["residential"]})
    estate_address: str = Field(..., description="Physical address", schema_extra={"examples": ["123 Main St"]})
    asset_id: str = Field(..., description="Asset category ID", schema_extra={"examples": ["AC-REAL-001"]})
    fx_code: str = Field(default="TWD", description="Currency code (TWD; USD/JPY/... for overseas property)", schema_extra={"examples": ["TWD"]})
    obtain_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20200101"]})
    loan_id: str | None = Field(default=None, description="Associated loan ID", schema_extra={"examples": ["LN-001"]})
    estate_status: EstateStatus = Field(..., description="Status", schema_extra={"examples": ["live"]})
    region: str | None = Field(default=None, description="House-price-index 縣市 (全國/臺北市/新北市/桃園市/臺中市/臺南市/高雄市); null → 全國", schema_extra={"examples": ["臺北市"]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["Primary residence"]})

    model_config = ConfigDict(json_schema_extra={"example": _ESTATE_EXAMPLE})


class EstateUpdate(SQLModel):
    estate_name: str | None = Field(default=None, description="Estate display name", schema_extra={"examples": ["Condo"]})
    estate_type: str | None = Field(default=None, description="Estate type", schema_extra={"examples": ["residential"]})
    estate_address: str | None = Field(default=None, description="Physical address", schema_extra={"examples": ["123 Main St"]})
    asset_id: str | None = Field(default=None, description="Asset category ID", schema_extra={"examples": ["AC-REAL-001"]})
    fx_code: str | None = Field(default=None, description="Currency code (TWD; USD/JPY/... for overseas property)", schema_extra={"examples": ["USD"]})
    obtain_date: str | None = Field(default=None, description="YYYYMMDD", schema_extra={"examples": ["20200101"]})
    loan_id: str | None = Field(default=None, description="Associated loan ID", schema_extra={"examples": ["LN-001"]})
    estate_status: EstateStatus | None = Field(default=None, description="Status", schema_extra={"examples": ["sold"]})
    region: str | None = Field(default=None, description="House-price-index 縣市 (全國/臺北市/新北市/桃園市/臺中市/臺南市/高雄市); null → 全國", schema_extra={"examples": ["臺北市"]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["Updated"]})

    model_config = ConfigDict(json_schema_extra={"example": {"estate_status": "sold"}})


class EstateRead(SQLModel):
    estate_id: str = Field(..., description="Estate business ID", schema_extra={"examples": ["EST-001"]})
    estate_name: str = Field(..., description="Estate display name", schema_extra={"examples": ["Condo"]})
    estate_type: str = Field(..., description="Estate type", schema_extra={"examples": ["residential"]})
    estate_address: str = Field(..., description="Physical address", schema_extra={"examples": ["123 Main St"]})
    asset_id: str = Field(..., description="Asset category ID", schema_extra={"examples": ["AC-REAL-001"]})
    fx_code: str = Field(default="TWD", description="Currency code (TWD; USD/JPY/... for overseas property)", schema_extra={"examples": ["TWD"]})
    obtain_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20200101"]})
    loan_id: str | None = Field(default=None, description="Associated loan ID", schema_extra={"examples": ["LN-001"]})
    estate_status: str = Field(..., description="Status", schema_extra={"examples": ["hold"]})
    region: str | None = Field(default=None, description="House-price-index 縣市 (全國/臺北市/新北市/桃園市/臺中市/臺南市/高雄市); null → 全國", schema_extra={"examples": ["臺北市"]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["Primary residence"]})

    model_config = ConfigDict(json_schema_extra={"example": _ESTATE_EXAMPLE})


class EstateJournal(SQLModel, table=True):
    __tablename__ = "Estate_Journal"

    distinct_number: int | None = Field(default=None, primary_key=True, description="Autoincrement PK", schema_extra={"examples": [1]})
    estate_id: str = Field(..., description="FK reference to Estate.estate_id", schema_extra={"examples": ["EST-001"]})
    estate_excute_type: str = Field(..., description="Transaction type (purchase / sale / ...)", schema_extra={"examples": ["purchase"]})
    excute_price: float = Field(..., description="Amount", schema_extra={"examples": [500000.0]})
    excute_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20200101"]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["Closing"]})

    model_config = ConfigDict(json_schema_extra={"example": _ESTATE_JOURNAL_EXAMPLE})


class EstateJournalCreate(SQLModel):
    estate_id: str = Field(..., description="FK to Estate.estate_id", schema_extra={"examples": ["EST-001"]})
    estate_excute_type: EstateExcuteType = Field(..., description="tax/fee/insurance/fix/rent/deposit", schema_extra={"examples": ["tax"]})
    excute_price: float = Field(..., description="Amount", schema_extra={"examples": [500000.0]})
    excute_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20200101"]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["Closing"]})

    model_config = ConfigDict(
        json_schema_extra={"example": {k: v for k, v in _ESTATE_JOURNAL_EXAMPLE.items() if k != "distinct_number"}}
    )


class EstateJournalUpdate(SQLModel):
    estate_excute_type: EstateExcuteType | None = Field(default=None, description="Transaction type", schema_extra={"examples": ["fee"]})
    excute_price: float | None = Field(default=None, description="Amount", schema_extra={"examples": [550000.0]})
    excute_date: str | None = Field(default=None, description="YYYYMMDD", schema_extra={"examples": ["20260101"]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["Updated"]})

    model_config = ConfigDict(json_schema_extra={"example": {"memo": "Updated"}})


class EstateJournalRead(SQLModel):
    distinct_number: int = Field(..., description="Autoincrement PK", schema_extra={"examples": [1]})
    estate_id: str = Field(..., description="FK to Estate.estate_id", schema_extra={"examples": ["EST-001"]})
    estate_excute_type: str = Field(..., description="Transaction type", schema_extra={"examples": ["purchase"]})
    excute_price: float = Field(..., description="Amount", schema_extra={"examples": [500000.0]})
    excute_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20200101"]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["Closing"]})

    model_config = ConfigDict(json_schema_extra={"example": _ESTATE_JOURNAL_EXAMPLE})
