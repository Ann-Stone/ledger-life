"""Budget model and CRUD schemas (Settings domain).

Composite PK: (budget_year, category_code). `category_code` is a FK to
`Code_Data.code_id`. `category_name` and `code_type` are intentionally
denormalized from `CodeData` — see BE-006 Notes.
"""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


_BUDGET_EXAMPLE = {
    "budget_year": "2026",
    "category_code": "INC01",
    "category_name": "Salary",
    "code_type": "income",
    "expected01": 100000.0,
    "expected02": 100000.0,
    "expected03": 100000.0,
    "expected04": 100000.0,
    "expected05": 100000.0,
    "expected06": 100000.0,
    "expected07": 100000.0,
    "expected08": 100000.0,
    "expected09": 100000.0,
    "expected10": 100000.0,
    "expected11": 100000.0,
    "expected12": 200000.0,
}


def _expected_field(month: str) -> object:
    return Field(
        ...,
        description=f"Expected amount for month {month}",
        schema_extra={"examples": [100000.0]},
    )


class Budget(SQLModel, table=True):
    __tablename__ = "Budget"

    budget_year: str = Field(
        ..., primary_key=True, description="YYYY", schema_extra={"examples": ["2026"]}
    )
    category_code: str = Field(
        ...,
        primary_key=True,
        foreign_key="Code_Data.code_id",
        description="FK to CodeData.code_id",
        schema_extra={"examples": ["INC01"]},
    )
    category_name: str = Field(
        ..., description="Denormalized category display name", schema_extra={"examples": ["Salary"]}
    )
    code_type: str = Field(
        ..., description="Denormalized code type (income / expense / ...)", schema_extra={"examples": ["income"]}
    )
    expected01: float = _expected_field("01")
    expected02: float = _expected_field("02")
    expected03: float = _expected_field("03")
    expected04: float = _expected_field("04")
    expected05: float = _expected_field("05")
    expected06: float = _expected_field("06")
    expected07: float = _expected_field("07")
    expected08: float = _expected_field("08")
    expected09: float = _expected_field("09")
    expected10: float = _expected_field("10")
    expected11: float = _expected_field("11")
    expected12: float = _expected_field("12")
    annual_amount: float | None = Field(
        default=None,
        description="Annual envelope for annual-event categories; null for ordinary categories",
        schema_extra={"examples": [None]},
    )

    model_config = ConfigDict(json_schema_extra={"example": _BUDGET_EXAMPLE})


class BudgetCreate(SQLModel):
    budget_year: str = Field(..., description="YYYY", schema_extra={"examples": ["2026"]})
    category_code: str = Field(..., description="FK to CodeData.code_id", schema_extra={"examples": ["INC01"]})
    category_name: str = Field(..., description="Category display name", schema_extra={"examples": ["Salary"]})
    code_type: str = Field(..., description="Code type", schema_extra={"examples": ["income"]})
    expected01: float = Field(..., description="Month 01 expected", schema_extra={"examples": [100000.0]})
    expected02: float = Field(..., description="Month 02 expected", schema_extra={"examples": [100000.0]})
    expected03: float = Field(..., description="Month 03 expected", schema_extra={"examples": [100000.0]})
    expected04: float = Field(..., description="Month 04 expected", schema_extra={"examples": [100000.0]})
    expected05: float = Field(..., description="Month 05 expected", schema_extra={"examples": [100000.0]})
    expected06: float = Field(..., description="Month 06 expected", schema_extra={"examples": [100000.0]})
    expected07: float = Field(..., description="Month 07 expected", schema_extra={"examples": [100000.0]})
    expected08: float = Field(..., description="Month 08 expected", schema_extra={"examples": [100000.0]})
    expected09: float = Field(..., description="Month 09 expected", schema_extra={"examples": [100000.0]})
    expected10: float = Field(..., description="Month 10 expected", schema_extra={"examples": [100000.0]})
    expected11: float = Field(..., description="Month 11 expected", schema_extra={"examples": [100000.0]})
    expected12: float = Field(..., description="Month 12 expected", schema_extra={"examples": [200000.0]})
    annual_amount: float | None = Field(
        default=None, description="Annual envelope for annual-event categories", schema_extra={"examples": [None]}
    )

    model_config = ConfigDict(json_schema_extra={"example": _BUDGET_EXAMPLE})


class BudgetUpdate(SQLModel):
    budget_year: str = Field(
        ...,
        description="Identifies the row along with category_code",
        schema_extra={"examples": ["2026"]},
    )
    category_code: str = Field(
        ...,
        description="Identifies the row along with budget_year",
        schema_extra={"examples": ["E01"]},
    )
    category_name: str | None = Field(default=None, description="Category display name", schema_extra={"examples": ["Salary"]})
    code_type: str | None = Field(default=None, description="Code type", schema_extra={"examples": ["income"]})
    expected01: float | None = Field(default=None, description="Month 01 expected", schema_extra={"examples": [100000.0]})
    expected02: float | None = Field(default=None, description="Month 02 expected", schema_extra={"examples": [100000.0]})
    expected03: float | None = Field(default=None, description="Month 03 expected", schema_extra={"examples": [100000.0]})
    expected04: float | None = Field(default=None, description="Month 04 expected", schema_extra={"examples": [100000.0]})
    expected05: float | None = Field(default=None, description="Month 05 expected", schema_extra={"examples": [100000.0]})
    expected06: float | None = Field(default=None, description="Month 06 expected", schema_extra={"examples": [100000.0]})
    expected07: float | None = Field(default=None, description="Month 07 expected", schema_extra={"examples": [100000.0]})
    expected08: float | None = Field(default=None, description="Month 08 expected", schema_extra={"examples": [100000.0]})
    expected09: float | None = Field(default=None, description="Month 09 expected", schema_extra={"examples": [100000.0]})
    expected10: float | None = Field(default=None, description="Month 10 expected", schema_extra={"examples": [100000.0]})
    expected11: float | None = Field(default=None, description="Month 11 expected", schema_extra={"examples": [100000.0]})
    expected12: float | None = Field(default=None, description="Month 12 expected", schema_extra={"examples": [200000.0]})
    annual_amount: float | None = Field(
        default=None, description="Annual envelope for annual-event categories", schema_extra={"examples": [None]}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"budget_year": "2026", "category_code": "E01", "expected12": 250000.0}
        }
    )


class BudgetRead(SQLModel):
    budget_year: str = Field(..., description="YYYY", schema_extra={"examples": ["2026"]})
    category_code: str = Field(..., description="FK to CodeData.code_id", schema_extra={"examples": ["INC01"]})
    category_name: str = Field(..., description="Category display name", schema_extra={"examples": ["Salary"]})
    code_type: str = Field(..., description="Code type", schema_extra={"examples": ["income"]})
    expected01: float = Field(..., description="Month 01 expected", schema_extra={"examples": [100000.0]})
    expected02: float = Field(..., description="Month 02 expected", schema_extra={"examples": [100000.0]})
    expected03: float = Field(..., description="Month 03 expected", schema_extra={"examples": [100000.0]})
    expected04: float = Field(..., description="Month 04 expected", schema_extra={"examples": [100000.0]})
    expected05: float = Field(..., description="Month 05 expected", schema_extra={"examples": [100000.0]})
    expected06: float = Field(..., description="Month 06 expected", schema_extra={"examples": [100000.0]})
    expected07: float = Field(..., description="Month 07 expected", schema_extra={"examples": [100000.0]})
    expected08: float = Field(..., description="Month 08 expected", schema_extra={"examples": [100000.0]})
    expected09: float = Field(..., description="Month 09 expected", schema_extra={"examples": [100000.0]})
    expected10: float = Field(..., description="Month 10 expected", schema_extra={"examples": [100000.0]})
    expected11: float = Field(..., description="Month 11 expected", schema_extra={"examples": [100000.0]})
    expected12: float = Field(..., description="Month 12 expected", schema_extra={"examples": [200000.0]})
    annual_amount: float | None = Field(
        default=None, description="Annual envelope for annual-event categories", schema_extra={"examples": [None]}
    )

    model_config = ConfigDict(json_schema_extra={"example": _BUDGET_EXAMPLE})
