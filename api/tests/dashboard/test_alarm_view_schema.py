"""BE-028 — alarm/gift view schema tests."""
from __future__ import annotations

from app.models.dashboard.alarm_view import AlarmItem


def test_alarm_item_example() -> None:
    js = AlarmItem.model_json_schema()
    assert "example" in js
    for n, p in js["properties"].items():
        assert "description" in p
