"""Tests for BE-022 Real-Estate asset CRUD + transaction details."""
from __future__ import annotations

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.assets.estate import (
    Estate,
    EstateCreate,
    EstateJournalCreate,
    EstateJournalUpdate,
    EstateUpdate,
)
from app.services.asset_service import (
    create_estate,
    create_estate_detail,
    delete_estate,
    delete_estate_detail,
    list_estate_details,
    list_estates,
    update_estate,
    update_estate_detail,
)


def _estate(estate_id: str = "EST-001", asset_id: str = "AC-REAL-001") -> EstateCreate:
    return EstateCreate(
        estate_id=estate_id,
        estate_name="Condo",
        estate_type="residential",
        estate_address="123 Main St",
        asset_id=asset_id,
        obtain_date="2024-01-15",
        loan_id=None,
        estate_status="live",
        memo="primary",
    )


def _detail(estate_id: str = "EST-001", excute_type: str = "tax") -> EstateJournalCreate:
    return EstateJournalCreate(
        estate_id=estate_id,
        estate_excute_type=excute_type,
        excute_price=15000.0,
        excute_date="2024-03-01",
        memo="seed",
    )


def test_schema_examples_present():
    for cls in (EstateCreate, EstateUpdate, EstateJournalCreate, EstateJournalUpdate):
        assert "example" in cls.model_config.get("json_schema_extra", {})


def test_list_estates_service(session: Session):
    create_estate(session, _estate("EST-001", "AC-REAL-001"))
    create_estate(session, _estate("EST-002", "AC-OTHER"))
    rows = list_estates(session, "AC-REAL-001")
    assert len(rows) == 1


def test_create_estate_service(session: Session):
    row = create_estate(session, _estate())
    assert row.obtain_date == "20240115"


def test_update_estate_404(session: Session):
    with pytest.raises(HTTPException) as exc:
        update_estate(session, "missing", EstateUpdate(estate_status="sold"))
    assert exc.value.status_code == 404


def test_delete_estate_service(session: Session):
    create_estate(session, _estate())
    delete_estate(session, "EST-001")
    assert session.get(Estate, "EST-001") is None


def test_list_estate_details_service(session: Session):
    create_estate(session, _estate())
    create_estate_detail(session, "EST-001", _detail())
    rows = list_estate_details(session, "EST-001")
    assert len(rows) == 1


def test_create_estate_detail_422_invalid_type(session: Session):
    with pytest.raises(Exception):
        EstateJournalCreate(
            estate_id="EST-001",
            estate_excute_type="bogus",
            excute_price=1.0,
            excute_date="2024-01-01",
        )


def test_update_estate_detail_404(session: Session):
    with pytest.raises(HTTPException) as exc:
        update_estate_detail(session, 9999, EstateJournalUpdate(memo="x"))
    assert exc.value.status_code == 404


def test_delete_estate_detail_service(session: Session):
    create_estate(session, _estate())
    d = create_estate_detail(session, "EST-001", _detail())
    delete_estate_detail(session, d.distinct_number)


def test_get_estates_happy(client: TestClient, session: Session):
    create_estate(session, _estate())
    resp = client.get("/assets/estates", params={"asset_id": "AC-REAL-001"})
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1


def test_post_estate_happy(client: TestClient):
    resp = client.post("/assets/estates", json=_estate().model_dump())
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["obtain_date"] == "20240115"


def test_put_estate_404(client: TestClient):
    resp = client.put("/assets/estates/missing", json={"estate_status": "sold"})
    assert resp.status_code == 404


def test_delete_estate_happy(client: TestClient, session: Session):
    create_estate(session, _estate())
    resp = client.delete("/assets/estates/EST-001")
    assert resp.status_code == 200


def test_get_estate_details_happy(client: TestClient, session: Session):
    create_estate(session, _estate())
    create_estate_detail(session, "EST-001", _detail())
    resp = client.get("/assets/estates/EST-001/details")
    assert resp.status_code == 200


def test_post_estate_detail_422_invalid_type(client: TestClient, session: Session):
    create_estate(session, _estate())
    payload = _detail().model_dump()
    payload["estate_excute_type"] = "bogus"
    resp = client.post("/assets/estates/EST-001/details", json=payload)
    assert resp.status_code == 422


def test_put_estate_detail_404(client: TestClient):
    resp = client.put("/assets/estates/details/9999", json={"memo": "x"})
    assert resp.status_code == 404


def test_delete_estate_detail_happy(client: TestClient, session: Session):
    create_estate(session, _estate())
    d = create_estate_detail(session, "EST-001", _detail())
    resp = client.delete(f"/assets/estates/details/{d.distinct_number}")
    assert resp.status_code == 200


def test_router_mounted(client: TestClient):
    resp = client.get("/assets/estates")
    assert resp.status_code == 422
