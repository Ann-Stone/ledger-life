"""Uncategorized-journal summary: type predicate, service aggregation, endpoint."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.monthly_report.analytics import UncategorizedSummaryResponse
from app.models.monthly_report.journal import Journal
from app.services.journal_types import is_uncategorized
from app.services.monthly_report_service import compute_uncategorized_summary


def _journal(vesting_month: str, action_main_type: str, **overrides) -> Journal:
    base = dict(
        vesting_month=vesting_month,
        spend_date=f"{vesting_month}15",
        spend_way="BANK-01",
        spend_way_type="account",
        spend_way_table="Account",
        action_main="1",
        action_main_type=action_main_type,
        action_main_table="Code_Data",
        spending=-100.0,
    )
    base.update(overrides)
    return Journal(**base)


# ---- Schema docs ----


def test_uncategorized_summary_schema() -> None:
    js = UncategorizedSummaryResponse.model_json_schema()
    assert "example" in js
    for n, p in js["properties"].items():
        assert "description" in p, n


# ---- Type predicate ----


def test_is_uncategorized_matches_report_buckets() -> None:
    # Legacy junk values are uncategorized.
    for value in ("undefined", "No", "", None, "Asset", "normal"):
        assert is_uncategorized(value), value
    # Every report bucket (any casing) is categorized.
    for value in ("Fixed", "floating", "Income", "Passive", "Invest", "Transfer"):
        assert not is_uncategorized(value), value


# ---- Service aggregation ----


def test_compute_uncategorized_summary(session: Session) -> None:
    session.add(_journal("202404", "undefined"))
    session.add(_journal("202404", "No"))
    session.add(_journal("202404", "Fixed"))      # categorized — not counted
    session.add(_journal("202405", ""))
    session.add(_journal("202406", "Income"))     # month with zero — omitted
    session.commit()

    summary = compute_uncategorized_summary(session)
    assert summary.total == 3
    # Newest month first; 202406 omitted entirely.
    assert [(m.vesting_month, m.count) for m in summary.months] == [
        ("202405", 1),
        ("202404", 2),
    ]


def test_compute_uncategorized_summary_empty(session: Session) -> None:
    summary = compute_uncategorized_summary(session)
    assert summary.total == 0
    assert summary.months == []


# ---- Endpoint (also proves the static route wins over /{vesting_month}) ----


def test_get_uncategorized_summary_endpoint(client: TestClient, session: Session) -> None:
    session.add(_journal("202405", "undefined"))
    session.commit()

    r = client.get("/monthly-report/journals/uncategorized-summary")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 1
    assert data["months"] == [{"vesting_month": "202405", "count": 1}]
