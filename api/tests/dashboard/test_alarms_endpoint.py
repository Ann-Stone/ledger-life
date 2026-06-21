"""BE-028 — alarms endpoint tests (Y/M recurrence only)."""
from __future__ import annotations

from datetime import datetime

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.settings.alarm import Alarm
from app.services.dashboard_service import get_upcoming_alarms


def test_monthly_expansion_within_horizon(session: Session) -> None:
    # Frozen "now" = 2026-04-15
    now = datetime(2026, 4, 15)
    session.add(
        Alarm(
            alarm_type="M",
            alarm_date="15",
            content="繳卡費",
            due_date="202606",  # YYYYMM cutoff: stop after June 2026
        )
    )
    session.commit()

    out = get_upcoming_alarms(session, now=now)
    dates = {item.date for item in out}
    # April through June expansion, July+ cut off by due_date
    assert "20260415" in dates
    assert "20260515" in dates
    assert "20260615" in dates
    assert "20260715" not in dates
    # All occurrences carry alarm_type=M
    assert all(item.alarm_type == "M" for item in out)


def test_monthly_expansion_clamps_end_of_month(session: Session) -> None:
    # Reminders set for the 31st should clamp to Feb 28 in non-leap years
    now = datetime(2026, 1, 1)
    session.add(Alarm(alarm_type="M", alarm_date="31", content="month-end"))
    session.commit()

    out = get_upcoming_alarms(session, now=now)
    feb = next(item for item in out if item.date.startswith("202602"))
    assert feb.date == "20260228"  # 2026 is non-leap


def test_yearly_expansion_returns_yyyymmdd(session: Session) -> None:
    now = datetime(2026, 4, 15)
    session.add(Alarm(alarm_type="Y", alarm_date="0531", content="報稅"))
    session.commit()

    out = get_upcoming_alarms(session, now=now)
    dates = {item.date for item in out}
    assert "20260531" in dates
    # Only one occurrence falls within 6-month horizon (2027/05/31 is too far)
    assert all(item.alarm_type == "Y" for item in out if item.content == "報稅")


def test_yearly_skips_past_anchor_in_current_year(session: Session) -> None:
    # If today is 2026-08-01 and the anchor is 05/31, this year's already gone;
    # 6-month horizon reaches 2027-02, which is before next year's 05/31 → no result.
    now = datetime(2026, 8, 1)
    session.add(Alarm(alarm_type="Y", alarm_date="0531", content="報稅"))
    session.commit()

    out = get_upcoming_alarms(session, now=now)
    assert all(item.content != "報稅" for item in out)


def test_yearly_crosses_year_boundary(session: Session) -> None:
    # November anchor on 0115: today 2025-11-15, horizon reaches 2026-05,
    # so the 2026-01-15 occurrence should appear.
    now = datetime(2025, 11, 15)
    session.add(Alarm(alarm_type="Y", alarm_date="0115", content="新年體檢"))
    session.commit()

    out = get_upcoming_alarms(session, now=now)
    assert any(item.date == "20260115" for item in out)


def test_list_alarms_endpoint_happy(client: TestClient, session: Session) -> None:
    session.add(Alarm(alarm_type="Y", alarm_date="0531", content="報稅"))
    session.commit()
    r = client.get("/dashboard/alarms")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == 1
    assert all(item["alarm_type"] in ("Y", "M") for item in body["data"])


def test_list_alarms_endpoint_empty(client: TestClient) -> None:
    r = client.get("/dashboard/alarms")
    assert r.status_code == 200
    assert r.json()["data"] == []
