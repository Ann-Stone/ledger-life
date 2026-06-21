"""Field-level tests for Account table."""
from __future__ import annotations

from app.models.settings.account import Account, AccountCreate, AccountUpdate, AccountRead


def test_account_table_fields() -> None:
    """Account exposes the full field set, correct PK/unique, and CRUD schemas."""
    table = Account.__table__

    assert Account.__tablename__ == "Account"

    # PK and unique business key
    assert table.c.id.primary_key is True
    assert table.c.account_id.unique is True
    assert table.c.account_id.index is True

    expected_columns = {
        "id",
        "account_id",
        "name",
        "account_type",
        "fx_code",
        "is_calculate",
        "in_use",
        "discount",
        "memo",
        "owner",
        "account_index",
    }
    assert set(table.c.keys()) == expected_columns

    # carrier_no is intentionally dropped (README Decision Log)
    assert "carrier_no" not in table.c

    # CRUD schema shape
    assert "id" not in AccountCreate.model_fields
    assert all(f.is_required() is False for f in AccountUpdate.model_fields.values())
    assert "id" in AccountRead.model_fields

    # JSON-schema discipline
    for schema_cls in (Account, AccountCreate, AccountUpdate, AccountRead):
        js = schema_cls.model_json_schema()
        assert "example" in js, f"{schema_cls.__name__} missing model example"
        for name, prop in js["properties"].items():
            assert "description" in prop, f"{schema_cls.__name__}.{name} missing description"
            assert "examples" in prop, f"{schema_cls.__name__}.{name} missing examples"
