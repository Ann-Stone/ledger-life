"""Field-level tests for CreditCard table."""
from __future__ import annotations

from app.models.settings.credit_card import (
    CreditCard,
    CreditCardCreate,
    CreditCardRead,
    CreditCardUpdate,
)


def test_credit_card_table_fields() -> None:
    table = CreditCard.__table__

    assert CreditCard.__tablename__ == "Credit_Card"
    assert table.c.credit_card_id.primary_key is True

    expected = {
        "credit_card_id",
        "card_name",
        "card_no",
        "last_day",
        "charge_day",
        "limit_date",
        "card_expiry",
        "feedback_way",
        "fx_code",
        "in_use",
        "credit_card_index",
        "note",
    }
    assert set(table.c.keys()) == expected

    # carrier_no intentionally dropped
    assert "carrier_no" not in table.c

    for schema_cls in (CreditCard, CreditCardCreate, CreditCardUpdate, CreditCardRead):
        js = schema_cls.model_json_schema()
        assert "example" in js
        for name, prop in js["properties"].items():
            assert "description" in prop, name
            assert "examples" in prop, name
