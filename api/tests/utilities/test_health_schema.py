"""Schema tests for HealthPayload."""
from __future__ import annotations

from app.models.utilities.health import HealthPayload


def test_health_schema_examples() -> None:
    schema = HealthPayload.model_json_schema()
    assert schema["properties"]["alive"]["examples"] == [True]
    assert schema["properties"]["version"]["examples"] == ["1.0.0"]
    assert schema["properties"]["alive"]["description"]
    assert schema["properties"]["version"]["description"]
    assert schema["example"] == {"alive": True, "version": "1.0.0"}
