"""Field-level tests for Journal table."""
from __future__ import annotations

from app.models.monthly_report.journal import (
    Journal,
    JournalCreate,
    JournalRead,
    JournalUpdate,
)


def test_journal_table_fields() -> None:
    table = Journal.__table__

    assert Journal.__tablename__ == "Journal"
    assert table.c.distinct_number.primary_key is True
    # autoincrement flag via sa_column_kwargs
    assert table.c.distinct_number.autoincrement is True

    expected = {
        "distinct_number",
        "vesting_month",
        "spend_date",
        "spend_way",
        "spend_way_type",
        "spend_way_table",
        "action_main",
        "action_main_type",
        "action_main_table",
        "action_sub",
        "action_sub_type",
        "action_sub_table",
        "spending",
        "invoice_number",
        "note",
    }
    assert set(table.c.keys()) == expected

    for schema_cls in (Journal, JournalCreate, JournalUpdate, JournalRead):
        js = schema_cls.model_json_schema()
        assert "example" in js
        for name, prop in js["properties"].items():
            assert "description" in prop, name
            assert "examples" in prop, name
