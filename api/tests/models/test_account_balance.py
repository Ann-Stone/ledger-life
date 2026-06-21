"""AccountBalance composite-PK test."""
from __future__ import annotations

from app.models.monthly_report.account_balance import (
    AccountBalance,
    AccountBalanceCreate,
    AccountBalanceRead,
    AccountBalanceUpdate,
)


def test_account_balance_composite_pk() -> None:
    table = AccountBalance.__table__

    assert AccountBalance.__tablename__ == "Account_Balance"
    pk = {c.name for c in table.primary_key.columns}
    assert pk == {"vesting_month", "id"}

    expected = {"vesting_month", "id", "name", "balance", "fx_code", "fx_rate", "is_calculate"}
    assert set(table.c.keys()) == expected

    for cls in (AccountBalance, AccountBalanceCreate, AccountBalanceUpdate, AccountBalanceRead):
        js = cls.model_json_schema()
        assert "example" in js
        for n, p in js["properties"].items():
            assert "description" in p, n
            assert "examples" in p, n
