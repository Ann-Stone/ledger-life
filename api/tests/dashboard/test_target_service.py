"""BE-027 — target service tests."""
from __future__ import annotations

from datetime import datetime

import pytest
from fastapi import HTTPException
from sqlmodel import Session

from app.models.dashboard.target_setting import (
    TargetSetting,
    TargetSettingCreate,
    TargetSettingUpdate,
)
from app.services.dashboard_service import (
    create_target,
    delete_target,
    list_targets,
    update_target,
)


def test_list_targets_returns_all(session: Session) -> None:
    create_target(
        session,
        TargetSettingCreate(setting_value="Save 1M", target_year="2025"),
    )
    create_target(
        session,
        TargetSettingCreate(setting_value="Save 2M", target_year="2026"),
    )
    rows = list_targets(session)
    # Ordered by target_year desc then distinct_number asc → 2026 row first
    assert [r.target_year for r in rows] == ["2026", "2025"]


def test_create_target_defaults_year_and_done(session: Session) -> None:
    out = create_target(session, TargetSettingCreate(setting_value="Save 500K"))
    assert out.target_year == datetime.now().strftime("%Y")
    assert out.is_done == "N"


def test_create_target_auto_assigns_sequential_id(session: Session) -> None:
    # Pre-seed with one numeric and one legacy non-numeric ID
    session.add(TargetSetting(distinct_number="5", target_year="2026", setting_value="x", is_done="N"))
    session.add(TargetSetting(distinct_number="legacy-id", target_year="2026", setting_value="y", is_done="N"))
    session.commit()
    out = create_target(session, TargetSettingCreate(setting_value="new"))
    # max numeric is 5, legacy ignored → next is "6"
    assert out.distinct_number == "6"


def test_update_target_is_done_only(session: Session) -> None:
    created = create_target(
        session,
        TargetSettingCreate(setting_value="Save 1M", target_year="2026"),
    )
    out = update_target(session, created.distinct_number, TargetSettingUpdate(is_done="Y"))
    assert out.is_done == "Y"
    assert out.setting_value == "Save 1M"
    assert out.target_year == "2026"


def test_update_target_missing(session: Session) -> None:
    with pytest.raises(HTTPException) as ei:
        update_target(session, "missing", TargetSettingUpdate(is_done="Y"))
    assert ei.value.status_code == 404


def test_delete_target_missing_returns_404(session: Session) -> None:
    with pytest.raises(HTTPException) as ei:
        delete_target(session, "missing")
    assert ei.value.status_code == 404
