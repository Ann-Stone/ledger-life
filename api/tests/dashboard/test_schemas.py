"""BE-026 — schema example smoke tests."""
from __future__ import annotations

from app.models.dashboard.budget import BudgetLine, BudgetRead, BudgetType
from app.models.dashboard.summary import SummaryPoint, SummaryRead, SummaryType


def _check(cls) -> None:
    js = cls.model_json_schema()
    assert "example" in js, cls.__name__
    for n, p in js["properties"].items():
        assert "description" in p, f"{cls.__name__}.{n}"


def test_summary_schema_example() -> None:
    _check(SummaryPoint)
    _check(SummaryRead)
    assert SummaryType.spending.value == "spending"


def test_budget_schema_example() -> None:
    _check(BudgetLine)
    _check(BudgetRead)
    assert BudgetType.monthly.value == "monthly"
