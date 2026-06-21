"""Tests for BE-024 OtherAsset CRUD endpoints."""
from __future__ import annotations

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.assets.other_asset import (
    OtherAsset,
    OtherAssetCreate,
    OtherAssetItem,
    OtherAssetUpdate,
)
from app.services.asset_service import (
    create_other_asset,
    delete_other_asset,
    list_other_asset_items,
    list_other_assets,
    update_other_asset,
)


def _payload(asset_id: str = "AC-STK-001", asset_type: str = "stock", asset_index: int | None = None) -> OtherAssetCreate:
    return OtherAssetCreate(
        asset_id=asset_id,
        asset_name="US equities",
        asset_type=asset_type,
        in_use="Y",
        asset_index=asset_index,
    )


def test_schema_examples_present():
    for cls in (OtherAssetCreate, OtherAssetUpdate, OtherAssetItem):
        assert "example" in cls.model_config.get("json_schema_extra", {})


def test_list_other_assets_ordered_by_index(session: Session):
    create_other_asset(session, _payload("AC-1", "stock", 5))
    create_other_asset(session, _payload("AC-2", "loan", 1))
    rows = list_other_assets(session)
    assert [r.asset_id for r in rows] == ["AC-2", "AC-1"]


def test_list_other_asset_items_distinct(session: Session):
    create_other_asset(session, _payload("AC-1", "stock"))
    create_other_asset(session, _payload("AC-2", "stock"))
    create_other_asset(session, _payload("AC-3", "loan"))
    items = list_other_asset_items(session)
    types = {i.asset_type for i in items}
    assert types == {"stock", "loan"}


def test_create_other_asset_auto_index(session: Session):
    a = create_other_asset(session, _payload("AC-1"))
    b = create_other_asset(session, _payload("AC-2"))
    assert a.asset_index == 1
    assert b.asset_index == 2


def test_update_other_asset_404(session: Session):
    with pytest.raises(HTTPException) as exc:
        update_other_asset(session, "missing", OtherAssetUpdate(in_use="N"))
    assert exc.value.status_code == 404


def test_delete_other_asset_service(session: Session):
    create_other_asset(session, _payload())
    delete_other_asset(session, "AC-STK-001")
    assert session.get(OtherAsset, "AC-STK-001") is None


def test_get_other_assets_happy(client: TestClient, session: Session):
    create_other_asset(session, _payload())
    resp = client.get("/assets/other-assets")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1


def test_get_other_asset_items_happy(client: TestClient, session: Session):
    create_other_asset(session, _payload())
    resp = client.get("/assets/other-assets/items")
    assert resp.status_code == 200
    assert resp.json()["data"][0]["asset_type"] == "stock"


def test_post_other_asset_happy(client: TestClient):
    resp = client.post("/assets/other-assets", json=_payload().model_dump())
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["asset_index"] == 1


def test_put_other_asset_404(client: TestClient):
    resp = client.put("/assets/other-assets/missing", json={"in_use": "N"})
    assert resp.status_code == 404


def test_delete_other_asset_happy(client: TestClient, session: Session):
    create_other_asset(session, _payload())
    resp = client.delete("/assets/other-assets/AC-STK-001")
    assert resp.status_code == 200


def test_router_mounted(client: TestClient):
    resp = client.get("/assets/other-assets")
    assert resp.status_code == 200
