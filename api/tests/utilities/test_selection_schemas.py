"""Schema-level tests for utility selection models."""
from __future__ import annotations

from app.models.utilities.selection import SelectionGroup, SelectionOption


def test_selection_schema_examples() -> None:
    option_schema = SelectionOption.model_json_schema()
    group_schema = SelectionGroup.model_json_schema()

    # Field-level examples present
    assert option_schema["properties"]["value"]["examples"] == ["1"]
    assert option_schema["properties"]["label"]["examples"] == ["Cash — NTD"]
    assert group_schema["properties"]["label"]["examples"] == ["BANK"]

    # Class-level full-model example present
    assert option_schema["example"] == {"value": "1", "label": "Cash — NTD"}
    assert group_schema["example"]["label"] == "BANK"
    assert group_schema["example"]["options"][0]["value"] == "1"

    # Field-level descriptions enforce documentation discipline
    assert option_schema["properties"]["value"]["description"]
    assert option_schema["properties"]["label"]["description"]
    assert group_schema["properties"]["label"]["description"]
    assert group_schema["properties"]["options"]["description"]
