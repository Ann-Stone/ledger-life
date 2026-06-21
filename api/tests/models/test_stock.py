"""Field-level tests for StockJournal and StockDetail tables."""
from __future__ import annotations

from app.models.assets.stock import (
    StockDetail,
    StockDetailCreate,
    StockDetailRead,
    StockDetailUpdate,
    StockJournal,
    StockJournalCreate,
    StockJournalRead,
    StockJournalUpdate,
)


def _check_doc_discipline(*classes) -> None:
    for cls in classes:
        js = cls.model_json_schema()
        assert "example" in js, cls.__name__
        for n, p in js["properties"].items():
            assert "description" in p, f"{cls.__name__}.{n}"
            assert "examples" in p, f"{cls.__name__}.{n}"


def test_stock_journal_fields() -> None:
    table = StockJournal.__table__
    assert StockJournal.__tablename__ == "Stock_Journal"
    assert table.c.stock_id.primary_key is True

    expected = {"stock_id", "stock_code", "stock_name", "asset_id", "expected_spend", "category_id"}
    assert set(table.c.keys()) == expected
    _check_doc_discipline(StockJournal, StockJournalCreate, StockJournalUpdate, StockJournalRead)


def test_stock_detail_fields() -> None:
    table = StockDetail.__table__
    assert StockDetail.__tablename__ == "Stock_Detail"
    assert table.c.distinct_number.primary_key is True

    expected = {
        "distinct_number",
        "stock_id",
        "excute_type",
        "excute_amount",
        "excute_price",
        "excute_date",
        "account_id",
        "account_name",
        "memo",
    }
    assert set(table.c.keys()) == expected
    _check_doc_discipline(StockDetail, StockDetailCreate, StockDetailUpdate, StockDetailRead)
