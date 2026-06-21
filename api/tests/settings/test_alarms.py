"""BE-014 — Alarm CRUD tests."""
from __future__ import annotations

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.settings.alarm import Alarm, AlarmCreate, AlarmRead, AlarmUpdate
from app.services.setting_service import (
    _normalize_due_date,
    create_alarm,
    delete_alarm,
    list_alarms,
    list_alarms_by_date,
    update_alarm,
)


def _payload(**overrides) -> dict:
    base = {
        "alarm_type": "Y",
        "alarm_date": "0826",
        "content": "Credit card payment",
        "due_date": "2026-05-01",
    }
    base.update(overrides)
    return base


def test_schema_examples() -> None:
    for cls in (Alarm, AlarmCreate, AlarmUpdate, AlarmRead):
        js = cls.model_json_schema()
        assert "example" in js
        for n, p in js["properties"].items():
            assert "description" in p, f"{cls.__name__}.{n}"
            assert "examples" in p, f"{cls.__name__}.{n}"


def test_normalize_due_date() -> None:
    assert _normalize_due_date(None) is None
    assert _normalize_due_date("") is None
    assert _normalize_due_date("2026-05-01") == "20260501"
    assert _normalize_due_date("20260501") == "20260501"
    assert _normalize_due_date("2026-05-01T12:34:56.000Z") == "20260501"
    with pytest.raises(HTTPException) as ei:
        _normalize_due_date("not-a-date")
    assert ei.value.status_code == 422


def test_list_service(session: Session) -> None:
    create_alarm(session, AlarmCreate(**_payload()))
    create_alarm(session, AlarmCreate(**_payload(content="Other")))
    rows = list_alarms(session)
    assert [r.alarm_id for r in rows] == sorted(r.alarm_id for r in rows)
    assert len(rows) == 2


def test_list_by_date(session: Session) -> None:
    create_alarm(session, AlarmCreate(**_payload(alarm_type="Y", alarm_date="0826")))
    create_alarm(session, AlarmCreate(**_payload(alarm_type="M", alarm_date="26")))
    create_alarm(session, AlarmCreate(**_payload(alarm_type="Y", alarm_date="0715")))
    rows = list_alarms_by_date(session, "26")
    assert {r.alarm_date for r in rows} == {"0826", "26"}


def test_create_normalizes_iso(session: Session) -> None:
    alarm = create_alarm(session, AlarmCreate(**_payload(due_date="2026-05-01T12:34:56.000Z")))
    assert alarm.due_date == "20260501"


def test_update_404(session: Session) -> None:
    with pytest.raises(HTTPException) as ei:
        update_alarm(session, 999, AlarmUpdate(content="x"))
    assert ei.value.status_code == 404


def test_delete_404(session: Session) -> None:
    with pytest.raises(HTTPException) as ei:
        delete_alarm(session, 999)
    assert ei.value.status_code == 404


def test_update_normalizes_due_date(session: Session) -> None:
    alarm = create_alarm(session, AlarmCreate(**_payload()))
    updated = update_alarm(session, alarm.alarm_id, AlarmUpdate(due_date="2027-01-15"))
    assert updated.due_date == "20270115"


# ---- routers ----


def test_router_mounted(client: TestClient) -> None:
    paths = set(client.app.openapi()["paths"].keys())
    assert {
        "/settings/alarms",
        "/settings/alarms/by-date",
        "/settings/alarms/{alarm_id}",
    } <= paths


def test_get_list_happy(client: TestClient, session: Session) -> None:
    create_alarm(session, AlarmCreate(**_payload()))
    res = client.get("/settings/alarms")
    assert res.status_code == 200
    assert len(res.json()["data"]) == 1


def test_by_date_endpoint(client: TestClient, session: Session) -> None:
    create_alarm(session, AlarmCreate(**_payload(alarm_type="Y", alarm_date="0826")))
    create_alarm(session, AlarmCreate(**_payload(alarm_type="M", alarm_date="26")))
    res = client.get("/settings/alarms/by-date", params={"date": "26"})
    assert res.status_code == 200
    assert {r["alarm_date"] for r in res.json()["data"]} == {"0826", "26"}


def test_post_happy(client: TestClient) -> None:
    res = client.post("/settings/alarms", json=_payload())
    assert res.status_code == 200
    assert res.json()["data"]["due_date"] == "20260501"


def test_post_unparseable_due_date_returns_422(client: TestClient) -> None:
    res = client.post("/settings/alarms", json=_payload(due_date="not-a-date"))
    assert res.status_code == 422


def test_post_missing_type_returns_422(client: TestClient) -> None:
    payload = _payload()
    payload.pop("alarm_type")
    res = client.post("/settings/alarms", json=payload)
    assert res.status_code == 422


def test_put_happy(client: TestClient, session: Session) -> None:
    alarm = create_alarm(session, AlarmCreate(**_payload()))
    res = client.put(f"/settings/alarms/{alarm.alarm_id}", json={"content": "Updated"})
    assert res.status_code == 200
    assert res.json()["data"]["content"] == "Updated"


def test_put_unknown_id_returns_404(client: TestClient) -> None:
    res = client.put("/settings/alarms/999", json={"content": "x"})
    assert res.status_code == 404


def test_delete_happy(client: TestClient, session: Session) -> None:
    alarm = create_alarm(session, AlarmCreate(**_payload()))
    res = client.delete(f"/settings/alarms/{alarm.alarm_id}")
    assert res.status_code == 200


def test_delete_unknown_id_returns_404(client: TestClient) -> None:
    res = client.delete("/settings/alarms/999")
    assert res.status_code == 404
