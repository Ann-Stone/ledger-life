"""DASH-B01 — work_freedom_ratio summary tests."""
from __future__ import annotations

import pytest
from sqlmodel import Session

from app.models.dashboard.summary import SummaryType
from app.models.monthly_report.journal import Journal
from app.services.dashboard_service import (
    get_summary,
    get_work_freedom_ratio_summary,
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
        spend_date="20230110",
        vesting_month="202301",
    )
    base.update(kw)
    return Journal(**base)


def test_work_freedom_ratio_happy_path_mixed(session: Session) -> None:
    """passive=3000, active=7000 → 0.3 (between 0 and 1)."""
    session.add(_journal(vesting_month="202301", action_main="I01", action_main_type="Income", spending=7000.0))
    session.add(_journal(vesting_month="202301", action_main="P01", action_main_type="Passive", spending=3000.0))
    session.commit()

    summary = get_work_freedom_ratio_summary(session, "202301-202301")
    point = summary.points[0]
    assert summary.type == SummaryType.work_freedom_ratio
    assert point.value == 0.3
    assert 0.0 < point.value < 1.0
    assert point.breakdown == {"passive": 3000.0, "active": 7000.0}


def test_work_freedom_ratio_zero_passive(session: Session) -> None:
    """No Passive rows → value is 0.0."""
    session.add(_journal(vesting_month="202301", action_main_type="Income", spending=5000.0))
    session.commit()

    summary = get_work_freedom_ratio_summary(session, "202301-202301")
    point = summary.points[0]
    assert point.value == 0.0
    assert point.breakdown == {"passive": 0.0, "active": 5000.0}


def test_work_freedom_ratio_zero_active(session: Session) -> None:
    """Only Passive rows → value is 1.0."""
    session.add(_journal(vesting_month="202301", action_main_type="Passive", spending=4200.0))
    session.commit()

    summary = get_work_freedom_ratio_summary(session, "202301-202301")
    point = summary.points[0]
    assert point.value == 1.0
    assert point.breakdown == {"passive": 4200.0, "active": 0.0}


def test_work_freedom_ratio_zero_everything(session: Session) -> None:
    """No Income or Passive rows → value is 0.0, denominator-zero guard."""
    summary = get_work_freedom_ratio_summary(session, "202301-202301")
    point = summary.points[0]
    assert point.value == 0.0
    assert point.breakdown == {"passive": 0.0, "active": 0.0}


def test_work_freedom_ratio_breakdown_matches_per_month_sums(session: Session) -> None:
    """Per-month breakdown keys equal the raw sums for that month."""
    session.add(_journal(vesting_month="202301", action_main="I01", action_main_type="Income", spending=1000.0))
    session.add(_journal(vesting_month="202301", action_main="P01", action_main_type="Passive", spending=500.0))
    session.add(_journal(vesting_month="202302", action_main="I01", action_main_type="Income", spending=2000.0))
    session.add(_journal(vesting_month="202302", action_main="P01", action_main_type="Passive", spending=2000.0))
    # Floating / Fixed rows must not pollute either bucket.
    session.add(_journal(vesting_month="202301", action_main="FL01", action_main_type="Floating", spending=-300.0))
    session.add(_journal(vesting_month="202302", action_main="F01", action_main_type="Fixed", spending=-800.0))
    session.commit()

    summary = get_work_freedom_ratio_summary(session, "202301-202302")
    by_period = {p.period: p for p in summary.points}

    p1 = by_period["202301"]
    assert p1.breakdown == {"passive": 500.0, "active": 1000.0}
    assert p1.value == pytest.approx(500.0 / 1500.0, abs=1e-4)

    p2 = by_period["202302"]
    assert p2.breakdown == {"passive": 2000.0, "active": 2000.0}
    assert p2.value == 0.5


def test_get_summary_dispatches_work_freedom_ratio(session: Session) -> None:
    out = get_summary(session, SummaryType.work_freedom_ratio, "202301-202301")
    assert out.type == SummaryType.work_freedom_ratio
    assert out.points[0].breakdown == {"passive": 0.0, "active": 0.0}


def test_freedom_ratio_denominator_includes_passive(session: Session) -> None:
    """DASH-B01 sub-task 5: freedom_ratio counts both Income and Passive as income."""
    from app.services.dashboard_service import get_freedom_ratio_summary
    from app.models.settings.code_data import CodeData

    session.add(CodeData(code_id="F01", code_type="Fixed", name="Rent", in_use="Y", code_index=1))
    session.add(_journal(vesting_month="202301", action_main_type="Income", spending=6000.0))
    session.add(_journal(vesting_month="202301", action_main_type="Passive", spending=4000.0))
    session.add(
        _journal(
            vesting_month="202301",
            action_main="F01",
            action_main_type="Fixed",
            spending=-2500.0,
        )
    )
    session.commit()

    summary = get_freedom_ratio_summary(session, "202301-202301")
    point = summary.points[0]
    # (10000 - 2500) / 10000 = 0.75 — Passive is folded into income denominator.
    assert point.value == 0.75
    assert point.breakdown == {"income": 10000.0, "fixed_expenses": 2500.0}
