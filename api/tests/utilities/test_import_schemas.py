"""Schema-level tests for import request/response models."""
from __future__ import annotations

import pytest

from app.models.utilities.imports import (
    ImportAcceptedResponse,
    ImportRequest,
    InvoiceImportError,
    InvoiceImportResult,
)


def test_import_schema_examples() -> None:
    for cls in (
        ImportRequest,
        ImportAcceptedResponse,
        InvoiceImportError,
        InvoiceImportResult,
    ):
        schema = cls.model_json_schema()
        assert "example" in schema, cls.__name__
        for name, prop in schema.get("properties", {}).items():
            # Either inline (string/int/bool) or $ref to a sub-schema with desc.
            if "$ref" in prop or prop.get("type") == "array" and "$ref" in prop.get("items", {}):
                assert "description" in prop, f"{cls.__name__}.{name}"
                continue
            assert "description" in prop, f"{cls.__name__}.{name}"


def test_period_pattern_accepts_yyyymm_and_empty() -> None:
    ImportRequest(period="202601")
    ImportRequest(period="")


def test_period_pattern_rejects_garbage() -> None:
    with pytest.raises(Exception):
        ImportRequest(period="2026-01")
    with pytest.raises(Exception):
        ImportRequest(period="abcd12")
