"""Field-level tests for CodeData table."""
from __future__ import annotations

from app.models.settings.code_data import (
    CodeData,
    CodeDataCreate,
    CodeDataRead,
    CodeDataUpdate,
)


def test_code_data_table_fields() -> None:
    table = CodeData.__table__

    assert CodeData.__tablename__ == "Code_Data"
    assert table.c.code_id.primary_key is True

    expected = {
        "code_id",
        "code_type",
        "name",
        "parent_id",
        "in_use",
        "code_index",
        "is_annual_event",
    }
    assert set(table.c.keys()) == expected

    for schema_cls in (CodeData, CodeDataCreate, CodeDataUpdate, CodeDataRead):
        js = schema_cls.model_json_schema()
        assert "example" in js
        for name, prop in js["properties"].items():
            assert "description" in prop, f"{schema_cls.__name__}.{name}"
            assert "examples" in prop, f"{schema_cls.__name__}.{name}"
