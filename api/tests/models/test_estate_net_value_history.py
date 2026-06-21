"""EstateNetValueHistory triple-composite-PK test."""
from __future__ import annotations

from app.models.monthly_report.estate_net_value_history import (
    EstateNetValueHistory,
    EstateNetValueHistoryCreate,
    EstateNetValueHistoryRead,
    EstateNetValueHistoryUpdate,
)


def test_triple_composite_pk() -> None:
    table = EstateNetValueHistory.__table__

    assert EstateNetValueHistory.__tablename__ == "Estate_Net_Value_History"
    pk = {c.name for c in table.primary_key.columns}
    assert pk == {"vesting_month", "id", "asset_id"}

    expected = {"vesting_month", "id", "asset_id", "name", "market_value", "cost", "estate_status", "fx_code", "fx_rate"}
    assert set(table.c.keys()) == expected

    for cls in (
        EstateNetValueHistory,
        EstateNetValueHistoryCreate,
        EstateNetValueHistoryUpdate,
        EstateNetValueHistoryRead,
    ):
        js = cls.model_json_schema()
        assert "example" in js
        for n, p in js["properties"].items():
            assert "description" in p, n
            assert "examples" in p, n
