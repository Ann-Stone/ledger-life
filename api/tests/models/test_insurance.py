"""Field-level tests for Insurance and InsuranceJournal tables."""
from __future__ import annotations

from app.models.assets.insurance import (
    Insurance,
    InsuranceCreate,
    InsuranceJournal,
    InsuranceJournalCreate,
    InsuranceJournalRead,
    InsuranceJournalUpdate,
    InsuranceRead,
    InsuranceUpdate,
)


def _check(*classes) -> None:
    for cls in classes:
        js = cls.model_json_schema()
        assert "example" in js, cls.__name__
        for n, p in js["properties"].items():
            assert "description" in p, f"{cls.__name__}.{n}"
            assert "examples" in p, f"{cls.__name__}.{n}"


def test_insurance_fields() -> None:
    table = Insurance.__table__
    assert Insurance.__tablename__ == "Insurance"
    assert table.c.insurance_id.primary_key is True

    expected = {
        "insurance_id",
        "insurance_name",
        "asset_id",
        "in_account",
        "out_account",
        "start_date",
        "end_date",
        "pay_type",
        "pay_day",
        "expected_spend",
        "has_closed",
    }
    assert set(table.c.keys()) == expected
    _check(Insurance, InsuranceCreate, InsuranceUpdate, InsuranceRead)


def test_insurance_journal_fields() -> None:
    table = InsuranceJournal.__table__
    assert InsuranceJournal.__tablename__ == "Insurance_Journal"
    assert table.c.distinct_number.primary_key is True

    expected = {"distinct_number", "insurance_id", "insurance_excute_type", "excute_price", "excute_date", "memo"}
    assert set(table.c.keys()) == expected
    _check(InsuranceJournal, InsuranceJournalCreate, InsuranceJournalUpdate, InsuranceJournalRead)
