"""Field-level tests for TargetSetting table."""
from __future__ import annotations

from app.models.dashboard.target_setting import (
    TargetSetting,
    TargetSettingCreate,
    TargetSettingRead,
    TargetSettingUpdate,
)


def test_target_setting_fields() -> None:
    table = TargetSetting.__table__
    assert TargetSetting.__tablename__ == "Target_Setting"
    assert table.c.distinct_number.primary_key is True

    expected = {"distinct_number", "target_year", "setting_value", "is_done"}
    assert set(table.c.keys()) == expected

    for cls in (TargetSetting, TargetSettingCreate, TargetSettingUpdate, TargetSettingRead):
        js = cls.model_json_schema()
        assert "example" in js, cls.__name__
        for n, p in js["properties"].items():
            assert "description" in p, f"{cls.__name__}.{n}"
            assert "examples" in p, f"{cls.__name__}.{n}"
