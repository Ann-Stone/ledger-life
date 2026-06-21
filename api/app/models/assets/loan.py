"""Loan asset models: Loan (master) + LoanJournal (repayment detail)."""
from __future__ import annotations

from typing import Literal

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

LoanExcuteType = Literal["principal", "interest", "increment", "fee"]


_LOAN_EXAMPLE = {
    "loan_id": "LN-001",
    "loan_name": "Mortgage",
    "loan_type": "mortgage",
    "account_id": "BANK-CHASE-01",
    "account_name": "Chase Checking",
    "interest_rate": 0.035,
    "period": 360,
    "apply_date": "20200101",
    "grace_expire_date": "20200401",
    "pay_day": 1,
    "amount": 250000.0,
    "repayed": 12500.0,
    "loan_index": 1,
}
_LOAN_JOURNAL_EXAMPLE = {
    "distinct_number": 1,
    "loan_id": "LN-001",
    "loan_excute_type": "repayment",
    "excute_price": 1500.0,
    "excute_date": "20260401",
    "memo": "April payment",
}


class Loan(SQLModel, table=True):
    __tablename__ = "Loan"

    loan_id: str = Field(..., primary_key=True, description="Loan business ID", schema_extra={"examples": ["LN-001"]})
    loan_name: str = Field(..., description="Loan display name", schema_extra={"examples": ["Mortgage"]})
    loan_type: str = Field(..., description="Loan type (mortgage / auto / ...)", schema_extra={"examples": ["mortgage"]})
    account_id: str = Field(..., description="Repayment account business ID", schema_extra={"examples": ["BANK-CHASE-01"]})
    account_name: str = Field(..., description="Repayment account display name", schema_extra={"examples": ["Chase Checking"]})
    interest_rate: float = Field(..., description="Annual interest rate (decimal)", schema_extra={"examples": [0.035]})
    period: int = Field(..., description="Loan period in months", schema_extra={"examples": [360]})
    apply_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20200101"]})
    grace_expire_date: str | None = Field(default=None, description="Grace period end, YYYYMMDD", schema_extra={"examples": ["20200401"]})
    pay_day: int = Field(..., description="Day of month for repayment", schema_extra={"examples": [1]})
    amount: float = Field(..., description="Original loan amount", schema_extra={"examples": [250000.0]})
    repayed: float = Field(..., description="Cumulative principal repaid", schema_extra={"examples": [12500.0]})
    loan_index: int = Field(..., description="Dropdown order, ORDER BY ASC", schema_extra={"examples": [1]})

    model_config = ConfigDict(json_schema_extra={"example": _LOAN_EXAMPLE})


class LoanCreate(SQLModel):
    loan_id: str = Field(..., description="Loan business ID", schema_extra={"examples": ["LN-001"]})
    loan_name: str = Field(..., description="Loan display name", schema_extra={"examples": ["Mortgage"]})
    loan_type: str = Field(..., description="Loan type", schema_extra={"examples": ["mortgage"]})
    account_id: str = Field(..., description="Repayment account business ID", schema_extra={"examples": ["BANK-CHASE-01"]})
    account_name: str = Field(..., description="Repayment account display name", schema_extra={"examples": ["Chase Checking"]})
    interest_rate: float = Field(..., description="Annual interest rate", schema_extra={"examples": [0.035]})
    period: int = Field(..., description="Loan period in months", schema_extra={"examples": [360]})
    apply_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20200101"]})
    grace_expire_date: str | None = Field(default=None, description="Grace period end", schema_extra={"examples": ["20200401"]})
    pay_day: int = Field(..., description="Day of month for repayment", schema_extra={"examples": [1]})
    amount: float = Field(..., description="Original loan amount", schema_extra={"examples": [250000.0]})
    repayed: float = Field(..., description="Cumulative principal repaid", schema_extra={"examples": [0.0]})
    loan_index: int = Field(..., description="Dropdown order", schema_extra={"examples": [1]})

    model_config = ConfigDict(json_schema_extra={"example": _LOAN_EXAMPLE})


class LoanUpdate(SQLModel):
    loan_name: str | None = Field(default=None, description="Loan display name", schema_extra={"examples": ["Mortgage"]})
    loan_type: str | None = Field(default=None, description="Loan type", schema_extra={"examples": ["mortgage"]})
    account_id: str | None = Field(default=None, description="Repayment account business ID", schema_extra={"examples": ["BANK-CHASE-01"]})
    account_name: str | None = Field(default=None, description="Repayment account display name", schema_extra={"examples": ["Chase Checking"]})
    interest_rate: float | None = Field(default=None, description="Annual interest rate", schema_extra={"examples": [0.035]})
    period: int | None = Field(default=None, description="Loan period in months", schema_extra={"examples": [360]})
    apply_date: str | None = Field(default=None, description="YYYYMMDD", schema_extra={"examples": ["20200101"]})
    grace_expire_date: str | None = Field(default=None, description="Grace period end", schema_extra={"examples": ["20200401"]})
    pay_day: int | None = Field(default=None, description="Day of month for repayment", schema_extra={"examples": [1]})
    amount: float | None = Field(default=None, description="Original loan amount", schema_extra={"examples": [250000.0]})
    repayed: float | None = Field(default=None, description="Cumulative principal repaid", schema_extra={"examples": [12500.0]})
    loan_index: int | None = Field(default=None, description="Dropdown order", schema_extra={"examples": [2]})

    model_config = ConfigDict(json_schema_extra={"example": {"repayed": 13000.0}})


class LoanRead(SQLModel):
    loan_id: str = Field(..., description="Loan business ID", schema_extra={"examples": ["LN-001"]})
    loan_name: str = Field(..., description="Loan display name", schema_extra={"examples": ["Mortgage"]})
    loan_type: str = Field(..., description="Loan type", schema_extra={"examples": ["mortgage"]})
    account_id: str = Field(..., description="Repayment account business ID", schema_extra={"examples": ["BANK-CHASE-01"]})
    account_name: str = Field(..., description="Repayment account display name", schema_extra={"examples": ["Chase Checking"]})
    interest_rate: float = Field(..., description="Annual interest rate", schema_extra={"examples": [0.035]})
    period: int = Field(..., description="Loan period in months", schema_extra={"examples": [360]})
    apply_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20200101"]})
    grace_expire_date: str | None = Field(default=None, description="Grace period end", schema_extra={"examples": ["20200401"]})
    pay_day: int = Field(..., description="Day of month for repayment", schema_extra={"examples": [1]})
    amount: float = Field(..., description="Original loan amount", schema_extra={"examples": [250000.0]})
    repayed: float = Field(..., description="Cumulative principal repaid", schema_extra={"examples": [12500.0]})
    loan_index: int = Field(..., description="Dropdown order", schema_extra={"examples": [1]})

    model_config = ConfigDict(json_schema_extra={"example": _LOAN_EXAMPLE})


class LoanJournal(SQLModel, table=True):
    __tablename__ = "Loan_Journal"

    distinct_number: int | None = Field(default=None, primary_key=True, description="Autoincrement PK", schema_extra={"examples": [1]})
    loan_id: str = Field(..., description="FK reference to Loan.loan_id", schema_extra={"examples": ["LN-001"]})
    loan_excute_type: str = Field(..., description="Repayment / interest / ...", schema_extra={"examples": ["repayment"]})
    excute_price: float = Field(..., description="Amount", schema_extra={"examples": [1500.0]})
    excute_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20260401"]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["April payment"]})

    model_config = ConfigDict(json_schema_extra={"example": _LOAN_JOURNAL_EXAMPLE})


class LoanJournalCreate(SQLModel):
    loan_id: str = Field(..., description="FK to Loan.loan_id", schema_extra={"examples": ["LN-001"]})
    loan_excute_type: LoanExcuteType = Field(..., description="principal/interest/increment/fee", schema_extra={"examples": ["principal"]})
    excute_price: float = Field(..., description="Amount", schema_extra={"examples": [1500.0]})
    excute_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20260401"]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["April payment"]})

    model_config = ConfigDict(
        json_schema_extra={"example": {k: v for k, v in _LOAN_JOURNAL_EXAMPLE.items() if k != "distinct_number"}}
    )


class LoanJournalUpdate(SQLModel):
    loan_excute_type: LoanExcuteType | None = Field(default=None, description="Execution type", schema_extra={"examples": ["principal"]})
    excute_price: float | None = Field(default=None, description="Amount", schema_extra={"examples": [1500.0]})
    excute_date: str | None = Field(default=None, description="YYYYMMDD", schema_extra={"examples": ["20260401"]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["Updated"]})

    model_config = ConfigDict(json_schema_extra={"example": {"memo": "Updated"}})


class LoanJournalRead(SQLModel):
    distinct_number: int = Field(..., description="Autoincrement PK", schema_extra={"examples": [1]})
    loan_id: str = Field(..., description="FK to Loan.loan_id", schema_extra={"examples": ["LN-001"]})
    loan_excute_type: str = Field(..., description="Execution type", schema_extra={"examples": ["repayment"]})
    excute_price: float = Field(..., description="Amount", schema_extra={"examples": [1500.0]})
    excute_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20260401"]})
    memo: str | None = Field(default=None, description="Free-form memo", schema_extra={"examples": ["April payment"]})

    model_config = ConfigDict(json_schema_extra={"example": _LOAN_JOURNAL_EXAMPLE})


class LoanSelectionRead(SQLModel):
    loan_id: str = Field(..., description="Loan business ID", schema_extra={"examples": ["LN-001"]})
    loan_name: str = Field(..., description="Loan display name", schema_extra={"examples": ["Mortgage"]})

    model_config = ConfigDict(
        json_schema_extra={"example": {"loan_id": "LN-001", "loan_name": "Mortgage"}}
    )
