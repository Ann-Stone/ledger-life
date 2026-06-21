"""Insurance asset models: Insurance (policy master) + InsuranceJournal (detail)."""
from __future__ import annotations

from typing import Literal

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

InsuranceExcuteType = Literal["pay", "cash", "return", "expect"]
HasClosed = Literal["Y", "N"]


_INSURANCE_EXAMPLE = {
    "insurance_id": "INS-001",
    "insurance_name": "Whole life policy",
    "asset_id": "AC-INS-001",
    "in_account": "BANK-CHASE-01",
    "out_account": "BANK-CHASE-01",
    "start_date": "20200101",
    "end_date": "20500101",
    "pay_type": "annual",
    "pay_day": "01/15",
    "expected_spend": 1200.0,
    "has_closed": "N",
}
_INSURANCE_JOURNAL_EXAMPLE = {
    "distinct_number": 1,
    "insurance_id": "INS-001",
    "insurance_excute_type": "pay",
    "excute_price": 1200.0,
    "excute_date": "20260115",
    "memo": "Annual premium",
}


class Insurance(SQLModel, table=True):
    __tablename__ = "Insurance"

    insurance_id: str = Field(..., primary_key=True, description="Policy business ID", schema_extra={"examples": ["INS-001"]})
    insurance_name: str = Field(..., description="Policy display name", schema_extra={"examples": ["Whole life policy"]})
    asset_id: str = Field(..., description="Asset category ID", schema_extra={"examples": ["AC-INS-001"]})
    in_account: str = Field(..., description="Paying account id", schema_extra={"examples": ["BANK-CHASE-01"]})
    out_account: str = Field(..., description="Disbursing account id", schema_extra={"examples": ["BANK-CHASE-01"]})
    start_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20200101"]})
    end_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20500101"]})
    pay_type: str = Field(..., description="Premium cadence (annual / monthly / ...)", schema_extra={"examples": ["annual"]})
    pay_day: str = Field(
        ...,
        max_length=23,
        description=(
            "Premium withdrawal date(s), free-form string whose shape "
            "depends on pay_type: monthly = 'DD' (e.g. '15'); annual = "
            "'MM/DD' (e.g. '01/19'); quarterly = comma-separated 'MM/DD' "
            "list (e.g. '01/19,04/19,07/19,10/19')."
        ),
        schema_extra={"examples": ["01/15"]},
    )
    expected_spend: float = Field(..., description="Expected premium per pay_type cadence (e.g. annual premium amount when pay_type='annual')", schema_extra={"examples": [1200.0]})
    has_closed: str = Field(..., description="Closed flag (Y/N)", schema_extra={"examples": ["N"]})

    model_config = ConfigDict(json_schema_extra={"example": _INSURANCE_EXAMPLE})


class InsuranceCreate(SQLModel):
    insurance_id: str = Field(..., description="Policy business ID", schema_extra={"examples": ["INS-001"]})
    insurance_name: str = Field(..., description="Policy display name", schema_extra={"examples": ["Whole life policy"]})
    asset_id: str = Field(..., description="Asset category ID", schema_extra={"examples": ["AC-INS-001"]})
    in_account: str = Field(..., description="Paying account id", schema_extra={"examples": ["BANK-CHASE-01"]})
    out_account: str = Field(..., description="Disbursing account id", schema_extra={"examples": ["BANK-CHASE-01"]})
    start_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20200101"]})
    end_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20500101"]})
    pay_type: str = Field(..., description="Premium cadence", schema_extra={"examples": ["annual"]})
    pay_day: str = Field(..., max_length=23, description="Premium date(s); 'DD' / 'MM/DD' / 'MM/DD,...' by pay_type", schema_extra={"examples": ["01/15"]})
    expected_spend: float = Field(..., description="Expected premium per pay_type cadence (e.g. annual premium amount when pay_type='annual')", schema_extra={"examples": [1200.0]})
    has_closed: HasClosed = Field(..., description="Closed flag (Y/N)", schema_extra={"examples": ["N"]})

    model_config = ConfigDict(json_schema_extra={"example": _INSURANCE_EXAMPLE})


class InsuranceUpdate(SQLModel):
    insurance_name: str | None = Field(default=None, description="Policy display name", schema_extra={"examples": ["Whole life policy"]})
    asset_id: str | None = Field(default=None, description="Asset category ID", schema_extra={"examples": ["AC-INS-001"]})
    in_account: str | None = Field(default=None, description="Paying account id", schema_extra={"examples": ["BANK-CHASE-01"]})
    out_account: str | None = Field(default=None, description="Disbursing account id", schema_extra={"examples": ["BANK-CHASE-01"]})
    start_date: str | None = Field(default=None, description="YYYYMMDD", schema_extra={"examples": ["20200101"]})
    end_date: str | None = Field(default=None, description="YYYYMMDD", schema_extra={"examples": ["20500101"]})
    pay_type: str | None = Field(default=None, description="Premium cadence", schema_extra={"examples": ["annual"]})
    pay_day: str | None = Field(default=None, max_length=23, description="Premium date(s); 'DD' / 'MM/DD' / 'MM/DD,...' by pay_type", schema_extra={"examples": ["01/15"]})
    expected_spend: float | None = Field(default=None, description="Expected premium per pay_type cadence (e.g. annual premium amount when pay_type='annual')", schema_extra={"examples": [1200.0]})
    has_closed: HasClosed | None = Field(default=None, description="Closed flag", schema_extra={"examples": ["Y"]})

    model_config = ConfigDict(json_schema_extra={"example": {"has_closed": "Y"}})


class InsuranceRead(SQLModel):
    insurance_id: str = Field(..., description="Policy business ID", schema_extra={"examples": ["INS-001"]})
    insurance_name: str = Field(..., description="Policy display name", schema_extra={"examples": ["Whole life policy"]})
    asset_id: str = Field(..., description="Asset category ID", schema_extra={"examples": ["AC-INS-001"]})
    in_account: str = Field(..., description="Paying account id", schema_extra={"examples": ["BANK-CHASE-01"]})
    out_account: str = Field(..., description="Disbursing account id", schema_extra={"examples": ["BANK-CHASE-01"]})
    start_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20200101"]})
    end_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20500101"]})
    pay_type: str = Field(..., description="Premium cadence", schema_extra={"examples": ["annual"]})
    pay_day: str = Field(..., max_length=23, description="Premium date(s); 'DD' / 'MM/DD' / 'MM/DD,...' by pay_type", schema_extra={"examples": ["01/15"]})
    expected_spend: float = Field(..., description="Expected premium per pay_type cadence (e.g. annual premium amount when pay_type='annual')", schema_extra={"examples": [1200.0]})
    has_closed: str = Field(..., description="Closed flag", schema_extra={"examples": ["N"]})

    model_config = ConfigDict(json_schema_extra={"example": _INSURANCE_EXAMPLE})


class InsuranceJournal(SQLModel, table=True):
    __tablename__ = "Insurance_Journal"

    distinct_number: int | None = Field(default=None, primary_key=True, description="Autoincrement PK", schema_extra={"examples": [1]})
    insurance_id: str = Field(..., description="FK reference to Insurance.insurance_id", schema_extra={"examples": ["INS-001"]})
    insurance_excute_type: str = Field(..., description="Execution type: pay (扣款) / cash (配息) / return (贖回) / expect (legacy 預期價值)", schema_extra={"examples": ["pay"]})
    excute_price: float = Field(..., description="Amount", schema_extra={"examples": [1200.0]})
    excute_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20260115"]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["Annual premium"]})

    model_config = ConfigDict(json_schema_extra={"example": _INSURANCE_JOURNAL_EXAMPLE})


class InsuranceJournalCreate(SQLModel):
    insurance_id: str = Field(..., description="FK to Insurance.insurance_id", schema_extra={"examples": ["INS-001"]})
    insurance_excute_type: InsuranceExcuteType = Field(..., description="pay/cash/return/expect", schema_extra={"examples": ["pay"]})
    excute_price: float = Field(..., description="Amount", schema_extra={"examples": [1200.0]})
    excute_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20260115"]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["Annual premium"]})

    model_config = ConfigDict(
        json_schema_extra={"example": {k: v for k, v in _INSURANCE_JOURNAL_EXAMPLE.items() if k != "distinct_number"}}
    )


class InsuranceJournalUpdate(SQLModel):
    insurance_excute_type: InsuranceExcuteType | None = Field(default=None, description="Execution type", schema_extra={"examples": ["cash"]})
    excute_price: float | None = Field(default=None, description="Amount", schema_extra={"examples": [1200.0]})
    excute_date: str | None = Field(default=None, description="YYYYMMDD", schema_extra={"examples": ["20260115"]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["Updated"]})

    model_config = ConfigDict(json_schema_extra={"example": {"memo": "Updated"}})


class InsuranceJournalRead(SQLModel):
    distinct_number: int = Field(..., description="Autoincrement PK", schema_extra={"examples": [1]})
    insurance_id: str = Field(..., description="FK to Insurance.insurance_id", schema_extra={"examples": ["INS-001"]})
    insurance_excute_type: str = Field(..., description="Execution type", schema_extra={"examples": ["pay"]})
    excute_price: float = Field(..., description="Amount", schema_extra={"examples": [1200.0]})
    excute_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20260115"]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["Annual premium"]})

    model_config = ConfigDict(json_schema_extra={"example": _INSURANCE_JOURNAL_EXAMPLE})
