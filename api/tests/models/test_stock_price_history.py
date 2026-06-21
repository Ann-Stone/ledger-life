"""Field-level tests for StockPriceHistory table."""
from __future__ import annotations

from app.models.dashboard.stock_price_history import (
    StockPriceHistory,
    StockPriceHistoryCreate,
    StockPriceHistoryRead,
    StockPriceHistoryUpdate,
)


def test_stock_price_history_composite_pk() -> None:
    table = StockPriceHistory.__table__
    assert StockPriceHistory.__tablename__ == "Stock_Price_History"
    pks = {c.name for c in table.primary_key.columns}
    assert pks == {"stock_code", "fetch_date"}

    expected = {"stock_code", "fetch_date", "open_price", "highest_price", "lowest_price", "close_price"}
    assert set(table.c.keys()) == expected

    for cls in (StockPriceHistory, StockPriceHistoryCreate, StockPriceHistoryUpdate, StockPriceHistoryRead):
        js = cls.model_json_schema()
        assert "example" in js, cls.__name__
        for n, p in js["properties"].items():
            assert "description" in p, f"{cls.__name__}.{n}"
            assert "examples" in p, f"{cls.__name__}.{n}"
