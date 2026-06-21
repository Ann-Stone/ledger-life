"""BE-025 — schema example smoke tests."""
from __future__ import annotations

from app.models.reports.asset_breakdown import AssetBreakdownRead, AssetShare
from app.models.reports.balance import (
    BalanceAssets,
    BalanceLiabilities,
    BalanceLine,
    BalanceSheetRead,
)
from app.models.reports.budget_variance import (
    BudgetVarianceRead,
    BudgetVarianceRow,
    BudgetVarianceSummary,
)
from app.models.reports.cash_flow import (
    CashFlowActivity,
    CashFlowItem,
    CashFlowPoint,
    CashFlowRead,
    CashFlowSummary,
)
from app.models.reports.expense_insights import (
    ExpenseInsightsRead,
    LargeTxn,
    YoYRow,
)
from app.models.reports.expenditure import ExpenditurePoint, ExpenditureTrendRead
from app.models.reports.expenditure_composition import (
    ExpenditureCategoryNode,
    ExpenditureCompositionRead,
    ExpenditureSubNode,
)
from app.models.reports.income_expense import (
    IncomeExpensePoint,
    IncomeExpenseReportRead,
    IncomeExpenseSummary,
)


def _has_example_and_field_docs(cls) -> None:
    js = cls.model_json_schema()
    assert "example" in js, cls.__name__
    for n, p in js["properties"].items():
        assert "description" in p, f"{cls.__name__}.{n}"


def test_balance_sheet_schema_example() -> None:
    for cls in (BalanceLine, BalanceAssets, BalanceLiabilities, BalanceSheetRead):
        _has_example_and_field_docs(cls)


def test_expenditure_schema_example() -> None:
    for cls in (ExpenditurePoint, ExpenditureTrendRead):
        _has_example_and_field_docs(cls)


def test_asset_breakdown_schema_example() -> None:
    for cls in (AssetShare, AssetBreakdownRead):
        _has_example_and_field_docs(cls)


def test_income_expense_schema_example() -> None:
    for cls in (IncomeExpensePoint, IncomeExpenseSummary, IncomeExpenseReportRead):
        _has_example_and_field_docs(cls)


def test_expenditure_composition_schema_example() -> None:
    for cls in (ExpenditureSubNode, ExpenditureCategoryNode, ExpenditureCompositionRead):
        _has_example_and_field_docs(cls)


def test_budget_variance_schema_example() -> None:
    for cls in (BudgetVarianceRow, BudgetVarianceSummary, BudgetVarianceRead):
        _has_example_and_field_docs(cls)


def test_cash_flow_schema_example() -> None:
    for cls in (CashFlowItem, CashFlowActivity, CashFlowPoint, CashFlowSummary, CashFlowRead):
        _has_example_and_field_docs(cls)


def test_expense_insights_schema_example() -> None:
    for cls in (YoYRow, LargeTxn, ExpenseInsightsRead):
        _has_example_and_field_docs(cls)
