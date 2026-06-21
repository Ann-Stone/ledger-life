"""Tests for BE-021 Insurance asset CRUD + transaction details."""
from __future__ import annotations

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.assets.insurance import (
    Insurance,
    InsuranceCreate,
    InsuranceJournalCreate,
    InsuranceJournalUpdate,
    InsuranceUpdate,
)
from app.services.asset_service import (
    _normalize_ymd,
    create_insurance,
    create_insurance_detail,
    delete_insurance,
    delete_insurance_detail,
    list_insurance_details,
    list_insurances,
    update_insurance,
    update_insurance_detail,
)


def _policy(insurance_id: str = "INS-001", asset_id: str = "AC-INS-001") -> InsuranceCreate:
    return InsuranceCreate(
        insurance_id=insurance_id,
        insurance_name="Whole life",
        asset_id=asset_id,
        in_account="BANK-CHASE-01",
        out_account="BANK-CHASE-01",
        start_date="2024-01-15",
        end_date="2050-01-15",
        pay_type="annual",
        pay_day="01/15",
        expected_spend=1200.0,
        has_closed="N",
    )


def _detail(insurance_id: str = "INS-001", excute_type: str = "pay", price: float = 1000.0) -> InsuranceJournalCreate:
    return InsuranceJournalCreate(
        insurance_id=insurance_id,
        insurance_excute_type=excute_type,
        excute_price=price,
        excute_date="2024-03-01",
        memo="seed",
    )


def test_schema_examples_present():
    for cls in (InsuranceCreate, InsuranceUpdate, InsuranceJournalCreate, InsuranceJournalUpdate):
        assert "example" in cls.model_config.get("json_schema_extra", {})


def test_normalize_ymd():
    assert _normalize_ymd("2024-01-15") == "20240115"
    assert _normalize_ymd("20240115") == "20240115"
    assert _normalize_ymd(None) is None
    with pytest.raises(HTTPException):
        _normalize_ymd("not-a-date")


def test_list_insurances_service(session: Session):
    create_insurance(session, _policy("INS-001", "AC-INS-001"))
    create_insurance(session, _policy("INS-002", "AC-INS-OTHER"))
    rows = list_insurances(session, "AC-INS-001")
    assert len(rows) == 1


def test_create_insurance_service(session: Session):
    row = create_insurance(session, _policy())
    # ISO 8601 normalized to YYYYMMDD
    assert row.start_date == "20240115"


def test_update_insurance_service(session: Session):
    create_insurance(session, _policy())
    updated = update_insurance(session, "INS-001", InsuranceUpdate(has_closed="Y"))
    assert updated.has_closed == "Y"


def test_update_insurance_404(session: Session):
    with pytest.raises(HTTPException) as exc:
        update_insurance(session, "missing", InsuranceUpdate(has_closed="Y"))
    assert exc.value.status_code == 404


def test_delete_insurance_service(session: Session):
    create_insurance(session, _policy())
    delete_insurance(session, "INS-001")
    assert session.get(Insurance, "INS-001") is None


def test_list_insurance_details_service(session: Session):
    create_insurance(session, _policy())
    create_insurance_detail(session, "INS-001", _detail())
    rows = list_insurance_details(session, "INS-001")
    assert len(rows) == 1


def test_create_insurance_detail_service(session: Session):
    create_insurance(session, _policy())
    d = create_insurance_detail(session, "INS-001", _detail())
    assert d.distinct_number is not None
    assert d.excute_date == "20240301"


def test_update_insurance_detail_service(session: Session):
    create_insurance(session, _policy())
    d = create_insurance_detail(session, "INS-001", _detail())
    updated = update_insurance_detail(session, d.distinct_number, InsuranceJournalUpdate(memo="new"))
    assert updated.memo == "new"


def test_delete_insurance_detail_service(session: Session):
    create_insurance(session, _policy())
    d = create_insurance_detail(session, "INS-001", _detail())
    delete_insurance_detail(session, d.distinct_number)


def test_get_insurances_happy(client: TestClient, session: Session):
    create_insurance(session, _policy())
    resp = client.get("/assets/insurances", params={"asset_id": "AC-INS-001"})
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1


def test_post_insurance_iso_date_persists_as_ymd(client: TestClient):
    resp = client.post("/assets/insurances", json=_policy().model_dump())
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["start_date"] == "20240115"


def test_put_insurance_404(client: TestClient):
    resp = client.put("/assets/insurances/missing", json={"has_closed": "Y"})
    assert resp.status_code == 404


def test_delete_insurance_happy(client: TestClient, session: Session):
    create_insurance(session, _policy())
    resp = client.delete("/assets/insurances/INS-001")
    assert resp.status_code == 200


def test_get_insurance_details_happy(client: TestClient, session: Session):
    create_insurance(session, _policy())
    create_insurance_detail(session, "INS-001", _detail())
    resp = client.get("/assets/insurances/INS-001/details")
    assert resp.status_code == 200


def test_post_insurance_detail_422_invalid_enum(client: TestClient, session: Session):
    create_insurance(session, _policy())
    payload = _detail().model_dump()
    payload["insurance_excute_type"] = "bogus"
    resp = client.post("/assets/insurances/INS-001/details", json=payload)
    assert resp.status_code == 422


def test_put_insurance_detail_404(client: TestClient):
    resp = client.put("/assets/insurances/details/9999", json={"memo": "x"})
    assert resp.status_code == 404


def test_delete_insurance_detail_happy(client: TestClient, session: Session):
    create_insurance(session, _policy())
    d = create_insurance_detail(session, "INS-001", _detail())
    resp = client.delete(f"/assets/insurances/details/{d.distinct_number}")
    assert resp.status_code == 200


def test_router_mounted(client: TestClient):
    resp = client.get("/assets/insurances")
    assert resp.status_code == 422


def test_insurance_transactions_golden(client: TestClient, session: Session):
    create_insurance(session, _policy())
    for excute_type, price in [("pay", 1000), ("pay", 1000), ("return", 500)]:
        d = InsuranceJournalCreate(
            insurance_id="INS-001",
            insurance_excute_type=excute_type,
            excute_price=price,
            excute_date="2024-03-01",
        )
        resp = client.post("/assets/insurances/INS-001/details", json=d.model_dump())
        assert resp.status_code == 200, resp.text

    resp = client.get("/assets/insurances/INS-001/details")
    rows = resp.json()["data"]
    assert len(rows) == 3
    # Aggregation: pay - return = 1000 + 1000 - 500 = 1500 net out
    net = sum(
        r["excute_price"] if r["insurance_excute_type"] == "pay" else -r["excute_price"]
        for r in rows
        if r["insurance_excute_type"] in {"pay", "return"}
    )
    assert net == 1500
