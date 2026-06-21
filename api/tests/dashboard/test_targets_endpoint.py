"""BE-027 — targets endpoint tests."""
from __future__ import annotations

from datetime import datetime

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.dashboard.target_setting import TargetSetting


def test_list_targets_happy(client: TestClient, session: Session) -> None:
    session.add(TargetSetting(distinct_number="T1", target_year="2026", setting_value="Save 1M", is_done="N"))
    session.commit()

    r = client.get("/dashboard/targets")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == 1
    assert body["data"][0]["distinct_number"] == "T1"


def test_create_target_happy(client: TestClient) -> None:
    r = client.post("/dashboard/targets", json={"setting_value": "Save 500K"})
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["target_year"] == datetime.now().strftime("%Y")
    assert data["is_done"] == "N"
    # First row → serial "1"
    assert data["distinct_number"] == "1"


def test_create_target_auto_increments(client: TestClient, session: Session) -> None:
    session.add(TargetSetting(distinct_number="5", target_year="2026", setting_value="x", is_done="N"))
    session.add(TargetSetting(distinct_number="legacy-id", target_year="2026", setting_value="y", is_done="N"))
    session.commit()
    r = client.post("/dashboard/targets", json={"setting_value": "new one"})
    assert r.status_code == 200
    # Numeric max is 5, non-numeric "legacy-id" is ignored → next is "6"
    assert r.json()["data"]["distinct_number"] == "6"


def test_update_target_happy(client: TestClient, session: Session) -> None:
    session.add(TargetSetting(distinct_number="T1", target_year="2026", setting_value="Save 1M", is_done="N"))
    session.commit()
    r = client.put("/dashboard/targets/T1", json={"setting_value": "Save 2M"})
    assert r.status_code == 200
    assert r.json()["data"]["setting_value"] == "Save 2M"


def test_update_target_is_done_only(client: TestClient, session: Session) -> None:
    session.add(TargetSetting(distinct_number="T1", target_year="2026", setting_value="Save 1M", is_done="N"))
    session.commit()
    r = client.put("/dashboard/targets/T1", json={"is_done": "Y"})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["is_done"] == "Y"
    assert data["setting_value"] == "Save 1M"
    assert data["target_year"] == "2026"


def test_delete_target_happy(client: TestClient, session: Session) -> None:
    session.add(TargetSetting(distinct_number="T1", target_year="2026", setting_value="Save 1M", is_done="N"))
    session.commit()
    r = client.delete("/dashboard/targets/T1")
    assert r.status_code == 200


def test_update_target_missing_returns_404(client: TestClient) -> None:
    r = client.put("/dashboard/targets/9999", json={"is_done": "Y"})
    assert r.status_code == 404


def test_delete_target_missing_returns_404(client: TestClient) -> None:
    r = client.delete("/dashboard/targets/9999")
    assert r.status_code == 404


def test_create_target_invalid_body_returns_422(client: TestClient) -> None:
    # setting_value is str(max_length=45) — exceeding the max triggers 422.
    r = client.post("/dashboard/targets", json={"setting_value": "x" * 46})
    assert r.status_code == 422
