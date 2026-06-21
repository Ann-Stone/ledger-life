"""Stock category dictionary — service + router CRUD tests."""
from __future__ import annotations

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.assets.stock import StockJournal
from app.models.assets.stock_category import (
    StockCategory,
    StockCategoryCreate,
    StockCategoryRead,
    StockCategoryUpdate,
)
from app.services.stock_category_service import (
    create_stock_category,
    delete_stock_category,
    list_stock_categories,
    update_stock_category,
)


def _holding(category_id: str | None, stock_id: str = "STK-1") -> StockJournal:
    return StockJournal(
        stock_id=stock_id,
        stock_code="AAPL",
        stock_name="Apple",
        asset_id="AC-1",
        expected_spend=1000.0,
        category_id=category_id,
    )


def test_schema_examples() -> None:
    for cls in (StockCategory, StockCategoryCreate, StockCategoryUpdate, StockCategoryRead):
        js = cls.model_json_schema()
        assert "example" in js, cls.__name__
        for n, p in js["properties"].items():
            assert "description" in p, f"{cls.__name__}.{n}"
            assert "examples" in p, f"{cls.__name__}.{n}"


def test_table_fields() -> None:
    table = StockCategory.__table__
    assert StockCategory.__tablename__ == "Stock_Category"
    assert table.c.category_id.primary_key is True
    assert set(table.c.keys()) == {"category_id", "name", "in_use", "category_index"}


# ---- service ----


def test_create_generates_sequential_ids(session: Session) -> None:
    a = create_stock_category(session, StockCategoryCreate(name="成長型"))
    b = create_stock_category(session, StockCategoryCreate(name="債券"))
    assert a.category_id == "SC-001"
    assert b.category_id == "SC-002"
    assert (a.category_index, b.category_index) == (1, 2)
    assert a.in_use == "Y"


def test_list_orders_by_index(session: Session) -> None:
    create_stock_category(session, StockCategoryCreate(name="B", category_index=2))
    create_stock_category(session, StockCategoryCreate(name="A", category_index=1))
    rows = list_stock_categories(session)
    assert [r.name for r in rows] == ["A", "B"]


def test_list_in_use_filter(session: Session) -> None:
    a = create_stock_category(session, StockCategoryCreate(name="A"))
    update_stock_category(session, a.category_id, StockCategoryUpdate(in_use="N"))
    create_stock_category(session, StockCategoryCreate(name="B"))
    assert [r.name for r in list_stock_categories(session, in_use="Y")] == ["B"]


def test_update_happy(session: Session) -> None:
    a = create_stock_category(session, StockCategoryCreate(name="成長型"))
    update_stock_category(session, a.category_id, StockCategoryUpdate(name="成長股"))
    assert session.get(StockCategory, a.category_id).name == "成長股"


def test_update_404(session: Session) -> None:
    with pytest.raises(HTTPException) as ei:
        update_stock_category(session, "SC-999", StockCategoryUpdate(name="x"))
    assert ei.value.status_code == 404


def test_delete_happy(session: Session) -> None:
    a = create_stock_category(session, StockCategoryCreate(name="A"))
    delete_stock_category(session, a.category_id)
    assert session.get(StockCategory, a.category_id) is None


def test_delete_404(session: Session) -> None:
    with pytest.raises(HTTPException) as ei:
        delete_stock_category(session, "SC-999")
    assert ei.value.status_code == 404


def test_delete_in_use_refused(session: Session) -> None:
    a = create_stock_category(session, StockCategoryCreate(name="成長型"))
    session.add(_holding(a.category_id))
    session.commit()
    with pytest.raises(HTTPException) as ei:
        delete_stock_category(session, a.category_id)
    assert ei.value.status_code == 409


# ---- routers ----


def test_routers_mounted(client: TestClient) -> None:
    paths = set(client.app.openapi()["paths"].keys())
    assert {"/settings/stock-categories", "/settings/stock-categories/{category_id}"} <= paths


def test_post_and_list(client: TestClient) -> None:
    res = client.post("/settings/stock-categories", json={"name": "成長型"})
    assert res.status_code == 200
    assert res.json()["data"]["category_id"] == "SC-001"
    res = client.get("/settings/stock-categories")
    assert res.json()["data"][0]["name"] == "成長型"


def test_put_happy(client: TestClient) -> None:
    client.post("/settings/stock-categories", json={"name": "成長型"})
    res = client.put("/settings/stock-categories/SC-001", json={"name": "成長股"})
    assert res.status_code == 200
    assert res.json()["data"]["name"] == "成長股"


def test_put_404(client: TestClient) -> None:
    res = client.put("/settings/stock-categories/SC-999", json={"name": "x"})
    assert res.status_code == 404


def test_delete_happy_router(client: TestClient) -> None:
    client.post("/settings/stock-categories", json={"name": "成長型"})
    res = client.delete("/settings/stock-categories/SC-001")
    assert res.status_code == 200


def test_delete_in_use_returns_409(client: TestClient, session: Session) -> None:
    client.post("/settings/stock-categories", json={"name": "成長型"})
    session.add(_holding("SC-001"))
    session.commit()
    res = client.delete("/settings/stock-categories/SC-001")
    assert res.status_code == 409
    assert res.json()["status"] == 0


def test_post_missing_name_422(client: TestClient) -> None:
    res = client.post("/settings/stock-categories", json={})
    assert res.status_code == 422
