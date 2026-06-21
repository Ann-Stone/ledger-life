"""Field-level tests for Estate and EstateJournal tables."""
from __future__ import annotations

from app.models.assets.estate import (
    Estate,
    EstateCreate,
    EstateJournal,
    EstateJournalCreate,
    EstateJournalRead,
    EstateJournalUpdate,
    EstateRead,
    EstateUpdate,
)


def _check(*classes) -> None:
    for cls in classes:
        js = cls.model_json_schema()
        assert "example" in js, cls.__name__
        for n, p in js["properties"].items():
            assert "description" in p, f"{cls.__name__}.{n}"
            assert "examples" in p, f"{cls.__name__}.{n}"


def test_estate_fields() -> None:
    table = Estate.__table__
    assert Estate.__tablename__ == "Estate"
    assert table.c.estate_id.primary_key is True

    expected = {
        "estate_id",
        "estate_name",
        "estate_type",
        "estate_address",
        "asset_id",
        "obtain_date",
        "loan_id",
        "estate_status",
        "fx_code",
        "region",
        "memo",
    }
    assert set(table.c.keys()) == expected
    _check(Estate, EstateCreate, EstateUpdate, EstateRead)


def test_estate_journal_fields() -> None:
    table = EstateJournal.__table__
    assert EstateJournal.__tablename__ == "Estate_Journal"
    assert table.c.distinct_number.primary_key is True

    expected = {"distinct_number", "estate_id", "estate_excute_type", "excute_price", "excute_date", "memo"}
    assert set(table.c.keys()) == expected
    _check(EstateJournal, EstateJournalCreate, EstateJournalUpdate, EstateJournalRead)
