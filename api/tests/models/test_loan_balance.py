"""LoanBalance composite-PK test."""
from __future__ import annotations

from app.models.monthly_report.loan_balance import (
    LoanBalance,
    LoanBalanceCreate,
    LoanBalanceRead,
    LoanBalanceUpdate,
)


def test_loan_balance_composite_pk() -> None:
    table = LoanBalance.__table__

    assert LoanBalance.__tablename__ == "Loan_Balance"
    pk = {c.name for c in table.primary_key.columns}
    assert pk == {"vesting_month", "id"}

    expected = {"vesting_month", "id", "name", "balance", "cost", "fx_code", "fx_rate"}
    assert set(table.c.keys()) == expected

    for cls in (LoanBalance, LoanBalanceCreate, LoanBalanceUpdate, LoanBalanceRead):
        js = cls.model_json_schema()
        assert "example" in js
        for n, p in js["properties"].items():
            assert "description" in p, n
            assert "examples" in p, n
