"""StockNetValueHistory triple-composite-PK test."""
from __future__ import annotations

from app.models.monthly_report.stock_net_value_history import (
    StockNetValueHistory,
    StockNetValueHistoryCreate,
    StockNetValueHistoryRead,
    StockNetValueHistoryUpdate,
)


def test_stock_net_value_history_pk() -> None:
    table = StockNetValueHistory.__table__

    # legacy typo `__tablestock_name__` is NOT replicated
    assert StockNetValueHistory.__tablename__ == "Stock_Net_Value_History"
    pk = {c.name for c in table.primary_key.columns}
    assert pk == {"vesting_month", "id", "asset_id"}

    expected = {
        "vesting_month",
        "id",
        "asset_id",
        "stock_code",
        "stock_name",
        "amount",
        "price",
        "cost",
        "fx_code",
        "fx_rate",
    }
    assert set(table.c.keys()) == expected

    for cls in (
        StockNetValueHistory,
        StockNetValueHistoryCreate,
        StockNetValueHistoryUpdate,
        StockNetValueHistoryRead,
    ):
        js = cls.model_json_schema()
        assert "example" in js
        for n, p in js["properties"].items():
            assert "description" in p, n
            assert "examples" in p, n
