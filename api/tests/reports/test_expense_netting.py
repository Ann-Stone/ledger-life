"""Net-then-floor aggregation: the shared primitive plus the report scenarios it
fixes (mis-typed inflows, 代買 offsets, symmetric income floor, cross-month nets).
"""
from __future__ import annotations

from sqlmodel import Session

from app.models.monthly_report.journal import Journal
from app.services.expense_netting import (
    category_net_by_bucket,
    floor_expense,
    floor_income,
)
from app.services.report_service import get_income_expense_report


def _journal(**overrides) -> Journal:
    base = dict(
        vesting_month="202606",
        spend_date="20260615",
        spend_way="A1",
        spend_way_type="account",
        spend_way_table="Account",
        action_main="FOOD",
        action_main_type="Floating",
        action_main_table="Code_Data",
        spending=-100.0,
    )
    base.update(overrides)
    return Journal(**base)


# ---------- pure helpers ----------


def test_floor_expense_and_income_are_mirror_floors() -> None:
    assert floor_expense(-1000.0) == 1000.0  # outflow → magnitude
    assert floor_expense(200.0) == 0.0       # net inflow → 0, never negative
    assert floor_expense(0.0) == 0.0
    assert floor_income(5000.0) == 5000.0    # inflow → magnitude
    assert floor_income(-1000.0) == 0.0      # net outflow → 0, never negative


def test_category_net_by_bucket_groups_signed_and_records_type() -> None:
    rows = [
        _journal(action_main="FOOD", action_main_type="Floating", spending=-1000.0),
        _journal(action_main="FOOD", action_main_type="Floating", spending=300.0),
        _journal(vesting_month="202607", action_main="RENT", action_main_type="Fixed", spending=-500.0),
    ]
    net, cat_type = category_net_by_bucket(
        rows, bucket_of=lambda j: j.vesting_month, amount_of=lambda j: j.spending
    )
    assert net[("202606", "FOOD")] == -700.0  # -1000 + 300, signed
    assert net[("202607", "RENT")] == -500.0
    assert cat_type == {"FOOD": "Floating", "RENT": "Fixed"}


# ---------- report scenarios (the cases agreed with the user) ----------


def _income_expense(session: Session):
    return get_income_expense_report(session, "monthly", "202612")


def test_daigou_same_month_nets_to_zero(session: Session) -> None:
    # Pay 1000 for a friend, fully reimbursed in the same category/month → 0 expense.
    session.add(_journal(spending=-1000.0))
    session.add(_journal(spending=1000.0))
    session.commit()
    report = _income_expense(session)
    point = {p.period: p for p in report.points}["202606"]
    assert point.floating == 0.0
    assert report.summary.total_expense == 0.0


def test_overrepaid_category_floors_to_zero_without_offsetting_others(session: Session) -> None:
    # FOOD reimbursed to a net inflow (+200) must contribute 0 — and must NOT
    # cancel a different category's real expense (RENT 500).
    session.add(_journal(action_main="FOOD", spending=-1000.0))
    session.add(_journal(action_main="FOOD", spending=1200.0))
    session.add(_journal(action_main="RENT", action_main_type="Fixed", spending=-500.0))
    session.commit()
    report = _income_expense(session)
    assert report.summary.total_expense == 500.0  # RENT only, FOOD floored to 0


def test_partial_reimbursement_counts_the_net_outflow(session: Session) -> None:
    session.add(_journal(spending=-1000.0))
    session.add(_journal(spending=300.0))
    session.commit()
    assert _income_expense(session).summary.total_expense == 700.0


def test_mistyped_inflow_does_not_inflate_expense(session: Session) -> None:
    # +300000 received cash filed under a Floating category — must not become expense.
    session.add(_journal(action_main="OTHER", spending=300000.0))
    session.commit()
    report = _income_expense(session)
    assert report.summary.total_expense == 0.0
    assert report.summary.total_income == 0.0  # a Floating category is not income


def test_income_category_refund_floors_to_zero(session: Session) -> None:
    # Symmetric: an income category whose refunds exceed income can't go negative.
    session.add(_journal(action_main="SAL", action_main_type="Income", spending=5000.0))
    session.add(_journal(action_main="SAL", action_main_type="Income", spending=-6000.0))
    session.commit()
    assert _income_expense(session).summary.total_income == 0.0


def test_cross_month_same_year_daigou_nets_in_summary_only(session: Session) -> None:
    # Pay in 202603, reimbursed in 202608 (same year, same category): the payout
    # month's point still shows the outflow, but the annual summary nets to 0.
    session.add(_journal(vesting_month="202603", spend_date="20260315", spending=-1000.0))
    session.add(_journal(vesting_month="202608", spend_date="20260815", spending=1000.0))
    session.commit()
    report = _income_expense(session)
    points = {p.period: p for p in report.points}
    assert points["202603"].floating == 1000.0  # payout month shows the outflow
    assert points["202608"].floating == 0.0      # reimbursement month floored
    assert report.summary.total_expense == 0.0   # annual netting resolves it


def test_passive_income_counts_toward_total_income(session: Session) -> None:
    session.add(_journal(action_main="SAL", action_main_type="Income", spending=4000.0))
    session.add(_journal(action_main="DIV", action_main_type="Passive", spending=1000.0))
    session.commit()
    assert _income_expense(session).summary.total_income == 5000.0
