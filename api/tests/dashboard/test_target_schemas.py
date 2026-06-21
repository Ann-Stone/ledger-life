"""BE-027 — TargetSetting CRUD schema tests."""
from __future__ import annotations

from app.models.dashboard.target_setting import (
    TargetSettingCreate,
    TargetSettingRead,
    TargetSettingUpdate,
)


def test_target_create_example() -> None:
    js = TargetSettingCreate.model_json_schema()
    assert "example" in js
    # Bare-minimum body must validate (target_year, is_done optional).
    obj = TargetSettingCreate(distinct_number="T-2026-01", setting_value="Goal")
    assert obj.target_year is None
    assert obj.is_done is None


def test_target_update_partial_allowed() -> None:
    obj = TargetSettingUpdate(is_done="Y")
    dumped = obj.model_dump(exclude_unset=True)
    assert dumped == {"is_done": "Y"}


def test_target_read_example() -> None:
    js = TargetSettingRead.model_json_schema()
    assert "example" in js
    for n, p in js["properties"].items():
        assert "description" in p
