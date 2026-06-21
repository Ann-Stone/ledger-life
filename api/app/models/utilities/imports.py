"""Schemas for the data-import endpoints."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ImportRequest(BaseModel):
    period: str = Field(
        ...,
        pattern=r"^\d{6}$|^$",
        description="Target period in YYYYMM. Empty string falls back to today.",
        examples=["202601"],
    )

    model_config = ConfigDict(json_schema_extra={"example": {"period": "202601"}})


class ImportAcceptedResponse(BaseModel):
    message: str = Field(
        ...,
        description="Human-readable confirmation that the import was scheduled",
        examples=["stock import started"],
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"message": "stock import started"}}
    )


class InvoiceImportError(BaseModel):
    line: int = Field(
        ...,
        description="1-based line number from the invoice CSV that failed",
        examples=[42],
    )
    reason: str = Field(
        ...,
        description="Short explanation of why the row was skipped or failed",
        examples=["malformed amount column"],
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"line": 42, "reason": "malformed amount column"}}
    )


class InvoiceImportMonth(BaseModel):
    month: str = Field(
        ...,
        description="Vesting month in YYYYMM, derived from each invoice's date",
        examples=["202603"],
    )
    imported: int = Field(
        ...,
        description="Number of journal rows inserted for this month",
        examples=[12],
    )
    skipped: int = Field(
        ...,
        description="Number of rows skipped (skip-list or duplicate) for this month",
        examples=[3],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"month": "202603", "imported": 12, "skipped": 3}
        }
    )


class InvoiceImportResult(BaseModel):
    imported: int = Field(
        ...,
        description="Number of journal rows successfully inserted",
        examples=[10],
    )
    skipped: int = Field(
        ...,
        description="Number of rows skipped (skip-list match or duplicate invoice)",
        examples=[3],
    )
    failed: int = Field(
        ...,
        description="Number of rows that raised an error during processing",
        examples=[1],
    )
    months: list[InvoiceImportMonth] = Field(
        default_factory=list,
        description="Per-month breakdown of imported/skipped counts, sorted by month",
        examples=[[{"month": "202603", "imported": 12, "skipped": 3}]],
    )
    errors: list[InvoiceImportError] = Field(
        ...,
        description="Per-row error details for failed rows",
        examples=[[{"line": 42, "reason": "malformed amount column"}]],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "imported": 10,
                "skipped": 3,
                "failed": 1,
                "months": [{"month": "202603", "imported": 12, "skipped": 3}],
                "errors": [{"line": 42, "reason": "malformed amount column"}],
            }
        }
    )
