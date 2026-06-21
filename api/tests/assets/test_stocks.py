"""Tests for BE-020 Stock asset CRUD + transaction details."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.assets.stock import (
    StockDetail,
    StockDetailCreate,
    StockDetailUpdate,
    StockJournal,
    StockJournalCreate,
    StockJournalUpdate,
)
from app.services.asset_service import (
    create_stock,
    create_stock_detail,
    delete_stock,
    delete_stock_detail,
    list_stock_details,
    list_stocks,
    update_stock,
    update_stock_detail,
)


def _holding(stock_id: str = "STK-H-001", asset_id: str = "AC-STK-001") -> StockJournalCreate:
    return StockJournalCreate(
        stock_id=stock_id,
        stock_code="AAPL",
        stock_name="Apple Inc.",
        asset_id=asset_id,
        expected_spend=10000.0,
    )


def _detail(stock_id: str = "STK-H-001", excute_type: str = "buy", date: str = "20260101") -> StockDetailCreate:
    return StockDetailCreate(
        stock_id=stock_id,
        excute_type=excute_type,
        excute_amount=100.0,
        excute_price=50.0,
        excute_date=date,
        account_id="BANK-CHASE-01",
        account_name="Chase Checking",
        memo="seed",
    )


def test_schema_examples_present():
    for cls in (StockJournalCreate, StockJournalUpdate, StockDetailCreate, StockDetailUpdate):
        assert "example" in cls.model_config.get("json_schema_extra", {})


def test_list_stocks_service(session: Session):
    create_stock(session, _holding("STK-H-001", "AC-STK-001"))
    create_stock(session, _holding("STK-H-002", "AC-STK-002"))
    rows = list_stocks(session, "AC-STK-001")
    assert len(rows) == 1
    assert rows[0].stock_id == "STK-H-001"


def test_create_stock_service(session: Session):
    holding = create_stock(session, _holding())
    assert holding.stock_id == "STK-H-001"
    assert session.get(StockJournal, "STK-H-001") is not None


def test_update_stock_service(session: Session):
    create_stock(session, _holding())
    updated = update_stock(session, "STK-H-001", StockJournalUpdate(expected_spend=12000.0))
    assert updated.expected_spend == 12000.0


def test_update_stock_404(session: Session):
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        update_stock(session, "missing", StockJournalUpdate(expected_spend=1.0))
    assert exc.value.status_code == 404


def test_delete_stock_service(session: Session):
    create_stock(session, _holding())
    delete_stock(session, "STK-H-001")
    assert session.get(StockJournal, "STK-H-001") is None


def test_list_stock_details_service(session: Session):
    create_stock(session, _holding())
    create_stock_detail(session, "STK-H-001", _detail(date="20260102"))
    create_stock_detail(session, "STK-H-001", _detail(date="20260101"))
    rows = list_stock_details(session, "STK-H-001")
    assert [r.excute_date for r in rows] == ["20260101", "20260102"]


def test_create_stock_detail_service(session: Session):
    create_stock(session, _holding())
    detail = create_stock_detail(session, "STK-H-001", _detail())
    assert detail.distinct_number is not None


def test_create_stock_detail_invalid_enum_raises():
    with pytest.raises(Exception):
        StockDetailCreate(
            stock_id="STK-H-001",
            excute_type="bogus",
            excute_amount=1.0,
            excute_price=1.0,
            excute_date="20260101",
            account_id="BANK-CHASE-01",
            account_name="Chase Checking",
        )


def test_update_stock_detail_service(session: Session):
    create_stock(session, _holding())
    d = create_stock_detail(session, "STK-H-001", _detail())
    updated = update_stock_detail(session, d.distinct_number, StockDetailUpdate(memo="changed"))
    assert updated.memo == "changed"


def test_update_stock_detail_404(session: Session):
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        update_stock_detail(session, 9999, StockDetailUpdate(memo="x"))
    assert exc.value.status_code == 404


def test_delete_stock_detail_service(session: Session):
    create_stock(session, _holding())
    d = create_stock_detail(session, "STK-H-001", _detail())
    delete_stock_detail(session, d.distinct_number)
    assert session.get(StockDetail, d.distinct_number) is None


# ---- router-level ----


def test_get_stocks_happy(client: TestClient, session: Session):
    create_stock(session, _holding())
    resp = client.get("/assets/stocks", params={"asset_id": "AC-STK-001"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == 1
    assert len(body["data"]) == 1


def test_post_stock_happy(client: TestClient):
    resp = client.post("/assets/stocks", json=_holding().model_dump())
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["stock_id"] == "STK-H-001"


def test_put_stock_404(client: TestClient):
    resp = client.put("/assets/stocks/missing", json={"expected_spend": 1.0})
    assert resp.status_code == 404


def test_delete_stock_happy(client: TestClient, session: Session):
    create_stock(session, _holding())
    resp = client.delete("/assets/stocks/STK-H-001")
    assert resp.status_code == 200


def test_get_stock_details_happy(client: TestClient, session: Session):
    create_stock(session, _holding())
    create_stock_detail(session, "STK-H-001", _detail())
    resp = client.get("/assets/stocks/STK-H-001/details")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1


def test_post_stock_detail_422_invalid_excute_type(client: TestClient, session: Session):
    create_stock(session, _holding())
    payload = _detail().model_dump()
    payload["excute_type"] = "bogus"
    resp = client.post("/assets/stocks/STK-H-001/details", json=payload)
    assert resp.status_code == 422


def test_put_stock_detail_404(client: TestClient):
    resp = client.put("/assets/stocks/details/9999", json={"memo": "x"})
    assert resp.status_code == 404


def test_delete_stock_detail_happy(client: TestClient, session: Session):
    create_stock(session, _holding())
    d = create_stock_detail(session, "STK-H-001", _detail())
    resp = client.delete(f"/assets/stocks/details/{d.distinct_number}")
    assert resp.status_code == 200


def test_router_mounted(client: TestClient):
    # Mounted routes return 422 (missing query) rather than 404.
    resp = client.get("/assets/stocks")
    assert resp.status_code == 422


def test_stock_transactions_golden(client: TestClient, session: Session):
    create_stock(session, _holding())
    # buy 100@50, buy 100@60, sell 50@70
    for excute_type, amt, price, date in [
        ("buy", 100, 50, "20260101"),
        ("buy", 100, 60, "20260201"),
        ("sell", 50, 70, "20260301"),
    ]:
        d = StockDetailCreate(
            stock_id="STK-H-001",
            excute_type=excute_type,
            excute_amount=amt,
            excute_price=price,
            excute_date=date,
            account_id="BANK-CHASE-01",
            account_name="Chase Checking",
        )
        resp = client.post("/assets/stocks/STK-H-001/details", json=d.model_dump())
        assert resp.status_code == 200, resp.text

    resp = client.get("/assets/stocks/STK-H-001/details")
    rows = resp.json()["data"]
    assert len(rows) == 3
    # net quantity = 100 + 100 - 50 = 150
    net_qty = sum(r["excute_amount"] if r["excute_type"] == "buy" else -r["excute_amount"] for r in rows if r["excute_type"] in {"buy", "sell"})
    assert net_qty == 150
