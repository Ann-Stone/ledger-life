"""Budget variance (預算 vs 實際) response schemas — Reports domain.

Annual expected (from Budget: sum of expected01..12, or annual_amount for
annual-event categories) vs actual (the year's FX-converted expense journals),
per expense category, plus a summary with a run-rate projection. Only Fixed and
Floating categories are included; income / invest / transfer are out of scope.
"""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

_ROW_EXAMPLE = {
    "code": "F01",
    "name": "居住",
    "type": "Fixed",
    "expected": 360000.0,
    "actual": 372000.0,
    "diff": 12000.0,
    "usage_rate": 1.0333,
}


class BudgetVarianceRow(SQLModel):
    code: str = Field(
        ..., description="Category code (action_main / Budget.category_code)", schema_extra={"examples": ["F01"]}
    )
    name: str = Field(..., description="Category display name", schema_extra={"examples": ["居住"]})
    type: str = Field(..., description="Code type: Fixed or Floating", schema_extra={"examples": ["Fixed"]})
    expected: float = Field(..., description="Annual budgeted amount", schema_extra={"examples": [360000.0]})
    actual: float = Field(
        ..., description="Actual expense for the year, FX-converted", schema_extra={"examples": [372000.0]}
    )
    diff: float = Field(
        ..., description="actual - expected (positive = over budget)", schema_extra={"examples": [12000.0]}
    )
    usage_rate: float = Field(
        ..., description="actual / expected (0 when expected == 0)", schema_extra={"examples": [1.0333]}
    )

    model_config = ConfigDict(json_schema_extra={"example": _ROW_EXAMPLE})


_SUMMARY_EXAMPLE = {
    "total_expected": 780000.0,
    "total_actual": 360000.0,
    "total_diff": -420000.0,
    "usage_rate": 0.4615,
    "elapsed_months": 6,
    "projected_total": 720000.0,
}


class BudgetVarianceSummary(SQLModel):
    total_expected: float = Field(
        ..., description="Sum of expected across expense categories", schema_extra={"examples": [780000.0]}
    )
    total_actual: float = Field(
        ..., description="Sum of actual across expense categories", schema_extra={"examples": [360000.0]}
    )
    total_diff: float = Field(
        ..., description="total_actual - total_expected", schema_extra={"examples": [-420000.0]}
    )
    usage_rate: float = Field(
        ..., description="total_actual / total_expected (0 when no budget)", schema_extra={"examples": [0.4615]}
    )
    elapsed_months: int = Field(
        ...,
        description="Highest month index (1-12) with expense data; 0 when none. Drives the projection.",
        schema_extra={"examples": [6]},
    )
    projected_total: float = Field(
        ...,
        description="Run-rate annualized actual: total_actual / elapsed_months * 12 (= total_actual once the year is complete)",
        schema_extra={"examples": [720000.0]},
    )

    model_config = ConfigDict(json_schema_extra={"example": _SUMMARY_EXAMPLE})


class BudgetVarianceRead(SQLModel):
    year: str = Field(..., description="Budget year YYYY", schema_extra={"examples": ["2026"]})
    rows: list[BudgetVarianceRow] = Field(
        ...,
        description="Per-category rows, ordered by actual descending",
        schema_extra={"examples": [[_ROW_EXAMPLE]]},
    )
    summary: BudgetVarianceSummary = Field(..., description="Totals and run-rate projection")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"year": "2026", "rows": [_ROW_EXAMPLE], "summary": _SUMMARY_EXAMPLE}
        }
    )
