"""InsuranceNetValueHistory triple-composite-PK test."""
from __future__ import annotations

from app.models.monthly_report.insurance_net_value_history import (
    InsuranceNetValueHistory,
    InsuranceNetValueHistoryCreate,
    InsuranceNetValueHistoryRead,
    InsuranceNetValueHistoryUpdate,
)


def test_triple_composite_pk() -> None:
    table = InsuranceNetValueHistory.__table__

    assert InsuranceNetValueHistory.__tablename__ == "Insurance_Net_Value_History"
    pk = {c.name for c in table.primary_key.columns}
    assert pk == {"vesting_month", "id", "asset_id"}

    expected = {"vesting_month", "id", "asset_id", "name", "surrender_value", "cost", "fx_code", "fx_rate"}
    assert set(table.c.keys()) == expected

    for cls in (
        InsuranceNetValueHistory,
        InsuranceNetValueHistoryCreate,
        InsuranceNetValueHistoryUpdate,
        InsuranceNetValueHistoryRead,
    ):
        js = cls.model_json_schema()
        assert "example" in js
        for n, p in js["properties"].items():
            assert "description" in p, n
            assert "examples" in p, n
