"""BE-026 / BE-028 — dashboard_service unit tests."""
from __future__ import annotations

import pytest
from fastapi import HTTPException
from sqlmodel import Session

from app.models.dashboard.budget import BudgetType
from app.models.dashboard.summary import SummaryType
from app.models.monthly_report.account_balance import AccountBalance
from app.models.monthly_report.journal import Journal
from app.models.monthly_report.loan_balance import LoanBalance
from app.models.settings.budget import Budget
from app.models.settings.code_data import CodeData
from app.services.dashboard_service import (
    get_asset_debt_trend,
    get_budget_usage,
    get_freedom_ratio_summary,
    get_spending_summary,
    get_summary,
    parse_summary_period,
)


def _journal(**kw) -> Journal:
    base = dict(
        spend_way="A1",
        spend_way_type="account",
        spend_way_table="Account",
        action_main="X01",
        action_main_type="Floating",
        action_main_table="Code_Data",
        spending=-100.0,
        spend_date="20260410",
        vesting_month="202604",
    )
    base.update(kw)
    return Journal(**base)


def test_parse_summary_period_valid_and_invalid() -> None:
    assert parse_summary_period("202301-202312") == ("202301", "202312")
    with pytest.raises(HTTPException) as ei:
        parse_summary_period("2023-2024")
    assert ei.value.status_code == 422
    with pytest.raises(HTTPException):
        parse_summary_period("202312-202301")


def test_get_spending_summary_golden(session: Session) -> None:
    session.add(_journal(vesting_month="202301", spending=-100.0))
    session.add(_journal(vesting_month="202301", action_main="F01", action_main_type="Fixed", spending=-50.0))
    session.add(_journal(vesting_month="202302", spending=-200.0))
    session.add(_journal(vesting_month="202301", action_main="I01", action_main_type="Income", spending=999.0))
    session.commit()

    summary = get_spending_summary(session, "202301-202303")
    by_period = {p.period: p.value for p in summary.points}
    assert by_period == {"202301": 150.0, "202302": 200.0, "202303": 0.0}
    assert summary.type == SummaryType.spending


def test_get_freedom_ratio_summary_golden(session: Session) -> None:
    session.add(CodeData(code_id="F01", code_type="Fixed", name="Rent", in_use="Y", code_index=1))
    session.add(_journal(vesting_month="202301", action_main_type="Income", spending=10000.0))
    session.add(_journal(vesting_month="202301", action_main="F01", action_main_type="Fixed", spending=-2500.0))
    session.commit()

    summary = get_freedom_ratio_summary(session, "202301-202301")
    # (10000 - 2500) / 10000 = 0.75
    assert summary.points[0].value == 0.75
    point = summary.points[0]
    assert point.breakdown == {"income": 10000.0, "fixed_expenses": 2500.0}
    # Recomputed ratio from raw breakdown matches stored value.
    recomputed = (
        point.breakdown["income"] - point.breakdown["fixed_expenses"]
    ) / point.breakdown["income"]
    assert point.value == pytest.approx(recomputed, abs=1e-4)


def test_get_freedom_ratio_zero_income(session: Session) -> None:
    summary = get_freedom_ratio_summary(session, "202301-202301")
    assert summary.points[0].value == 0.0
    assert summary.points[0].breakdown == {"income": 0.0, "fixed_expenses": 0.0}


def test_get_asset_debt_trend_golden(session: Session) -> None:
    session.add(
        AccountBalance(
            vesting_month="202301",
            id="A1",
            name="Bank",
            balance=100000.0,
            fx_code="TWD",
            fx_rate=1.0,
            is_calculate="Y",
        )
    )
    session.add(LoanBalance(vesting_month="202301", id="L1", name="Loan", balance=-30000.0, cost=0.0, fx_code="TWD", fx_rate=1.0))
    session.commit()

    summary = get_asset_debt_trend(session, "202301-202302")
    by_period = {p.period: p.value for p in summary.points}
    # Both months use the latest <= month value (only 202301 row exists).
    assert by_period["202301"] == 70000.0
    assert by_period["202302"] == 70000.0

    expected_keys = {"accounts", "stocks", "estates", "insurances", "loans", "cards"}
    for p in summary.points:
        assert p.breakdown is not None
        assert set(p.breakdown.keys()) == expected_keys
        assert sum(p.breakdown.values()) == pytest.approx(p.value, abs=0.01)
        assert p.breakdown["loans"] <= 0
        assert p.breakdown["cards"] <= 0
    # Specific category attribution: account contributes +100k, loan contributes -30k
    assert summary.points[0].breakdown["accounts"] == 100000.0
    assert summary.points[0].breakdown["loans"] == -30000.0


def test_breakdown_is_none_for_spending_summary(session: Session) -> None:
    """spending variant does not expose a per-category breakdown."""
    session.add(_journal(vesting_month="202301", spending=-100.0))
    session.commit()
    summary = get_spending_summary(session, "202301-202302")
    assert all(p.breakdown is None for p in summary.points)


def test_get_summary_dispatches(session: Session) -> None:
    out = get_summary(session, SummaryType.spending, "202301-202301")
    assert out.type == SummaryType.spending
    out = get_summary(session, SummaryType.freedom_ratio, "202301-202301")
    assert out.type == SummaryType.freedom_ratio
    out = get_summary(session, SummaryType.asset_debt_trend, "202301-202301")
    assert out.type == SummaryType.asset_debt_trend


def test_get_budget_usage_golden(session: Session) -> None:
    session.add(
        Budget(
            budget_year="2026",
            category_code="F01",
            category_name="Rent",
            code_type="Fixed",
            **{f"expected{m:02d}": 10000.0 if m == 4 else 0.0 for m in range(1, 13)},
        )
    )
    session.add(_journal(vesting_month="202604", action_main="F01", spending=-8500.0))
    session.commit()

    out = get_budget_usage(session, BudgetType.monthly, "202604")
    # Single category line
    line = next(l for l in out.lines if l.category == "Rent")
    assert line.planned == 10000.0
    assert line.actual == 8500.0
    assert line.usage_pct == 85.0
    assert out.total_planned == 10000.0
    assert out.total_actual == 8500.0


def test_get_budget_usage_yearly(session: Session) -> None:
    session.add(
        Budget(
            budget_year="2026",
            category_code="F01",
            category_name="Rent",
            code_type="Fixed",
            **{f"expected{m:02d}": 1000.0 for m in range(1, 13)},
        )
    )
    session.commit()
    out = get_budget_usage(session, BudgetType.yearly, "2026")
    assert out.total_planned == 12000.0


def test_get_budget_usage_invalid_period(session: Session) -> None:
    with pytest.raises(HTTPException) as ei:
        get_budget_usage(session, BudgetType.monthly, "2026")
    assert ei.value.status_code == 422
    with pytest.raises(HTTPException):
        get_budget_usage(session, BudgetType.yearly, "202604")
