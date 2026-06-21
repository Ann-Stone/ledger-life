"""Budget composite-PK + FK test."""
from __future__ import annotations

from app.models.settings.budget import Budget, BudgetCreate, BudgetRead, BudgetUpdate


def test_budget_composite_pk_and_fk() -> None:
    table = Budget.__table__

    assert Budget.__tablename__ == "Budget"

    pk_cols = {c.name for c in table.primary_key.columns}
    assert pk_cols == {"budget_year", "category_code"}

    fks = list(table.c.category_code.foreign_keys)
    assert len(fks) == 1
    assert fks[0].target_fullname == "Code_Data.code_id"

    # All 12 expected{MM} columns present
    for mm in (f"{m:02d}" for m in range(1, 13)):
        assert f"expected{mm}" in table.c

    # Annual-event envelope column present
    assert "annual_amount" in table.c

    for schema_cls in (Budget, BudgetCreate, BudgetUpdate, BudgetRead):
        js = schema_cls.model_json_schema()
        assert "example" in js
        for name, prop in js["properties"].items():
            assert "description" in prop, name
            assert "examples" in prop, name
