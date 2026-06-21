"""Field-level tests for Alarm table."""
from __future__ import annotations

from app.models.settings.alarm import Alarm, AlarmCreate, AlarmRead, AlarmUpdate


def test_alarm_table_fields() -> None:
    table = Alarm.__table__

    assert Alarm.__tablename__ == "Alarm"
    assert table.c.alarm_id.primary_key is True

    expected = {"alarm_id", "alarm_type", "alarm_date", "content", "due_date"}
    assert set(table.c.keys()) == expected

    for schema_cls in (Alarm, AlarmCreate, AlarmUpdate, AlarmRead):
        js = schema_cls.model_json_schema()
        assert "example" in js
        for name, prop in js["properties"].items():
            assert "description" in prop, name
            assert "examples" in prop, name
