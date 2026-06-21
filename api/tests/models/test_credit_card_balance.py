"""CreditCardBalance composite-PK test."""
from __future__ import annotations

from app.models.monthly_report.credit_card_balance import (
    CreditCardBalance,
    CreditCardBalanceCreate,
    CreditCardBalanceRead,
    CreditCardBalanceUpdate,
)


def test_credit_card_balance_composite_pk() -> None:
    table = CreditCardBalance.__table__

    assert CreditCardBalance.__tablename__ == "Credit_Card_Balance"
    pk = {c.name for c in table.primary_key.columns}
    assert pk == {"vesting_month", "id"}

    expected = {"vesting_month", "id", "name", "balance", "fx_rate"}
    assert set(table.c.keys()) == expected

    for cls in (CreditCardBalance, CreditCardBalanceCreate, CreditCardBalanceUpdate, CreditCardBalanceRead):
        js = cls.model_json_schema()
        assert "example" in js
        for n, p in js["properties"].items():
            assert "description" in p, n
            assert "examples" in p, n
