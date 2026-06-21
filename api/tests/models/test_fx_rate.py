"""Field-level tests for FXRate table."""
from __future__ import annotations

from app.models.dashboard.fx_rate import (
    FXRate,
    FXRateCreate,
    FXRateRead,
    FXRateUpdate,
)


def test_fx_rate_composite_pk() -> None:
    table = FXRate.__table__
    assert FXRate.__tablename__ == "FX_Rate"
    pks = {c.name for c in table.primary_key.columns}
    assert pks == {"import_date", "code"}

    expected = {"import_date", "code", "buy_rate"}
    assert set(table.c.keys()) == expected

    for cls in (FXRate, FXRateCreate, FXRateUpdate, FXRateRead):
        js = cls.model_json_schema()
        assert "example" in js, cls.__name__
        for n, p in js["properties"].items():
            assert "description" in p, f"{cls.__name__}.{n}"
            assert "examples" in p, f"{cls.__name__}.{n}"
