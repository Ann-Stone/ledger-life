"""Tests for BE-023 Loan / Liability CRUD + transaction details."""
from __future__ import annotations

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.assets.loan import (
    Loan,
    LoanCreate,
    LoanJournalCreate,
    LoanJournalUpdate,
    LoanSelectionRead,
    LoanUpdate,
)
from app.services.asset_service import (
    _recalculate_repayed,
    create_loan,
    create_loan_detail,
    delete_loan,
    delete_loan_detail,
    get_loan,
    list_loan_details,
    list_loan_selection,
    list_loans,
    update_loan,
    update_loan_detail,
)


def _loan(loan_id: str = "LN-001", index: int = 1, amount: float = 1_000_000) -> LoanCreate:
    return LoanCreate(
        loan_id=loan_id,
        loan_name="Mortgage",
        loan_type="mortgage",
        account_id="BANK-CHASE-01",
        account_name="Chase Checking",
        interest_rate=0.0185,
        period=360,
        apply_date="2023-06-01",
        grace_expire_date="2024-06-01",
        pay_day=1,
        amount=amount,
        repayed=0.0,
        loan_index=index,
    )


def _detail(loan_id: str = "LN-001", excute_type: str = "principal", price: float = 100_000) -> LoanJournalCreate:
    return LoanJournalCreate(
        loan_id=loan_id,
        loan_excute_type=excute_type,
        excute_price=price,
        excute_date="2024-03-01",
        memo="seed",
    )


def test_schema_examples_present():
    for cls in (LoanCreate, LoanUpdate, LoanJournalCreate, LoanJournalUpdate, LoanSelectionRead):
        assert "example" in cls.model_config.get("json_schema_extra", {})


def test_list_loans_service(session: Session):
    create_loan(session, _loan("LN-001", index=2))
    create_loan(session, _loan("LN-002", index=1))
    rows = list_loans(session)
    assert [r.loan_id for r in rows] == ["LN-002", "LN-001"]


def test_get_loan_404(session: Session):
    with pytest.raises(HTTPException) as exc:
        get_loan(session, "missing")
    assert exc.value.status_code == 404


def test_loan_selection_service(session: Session):
    create_loan(session, _loan())
    rows = list_loan_selection(session)
    assert rows[0].loan_id == "LN-001"


def test_create_loan_service(session: Session):
    row = create_loan(session, _loan())
    assert row.apply_date == "20230601"
    assert row.repayed == 0.0


def test_update_loan_404(session: Session):
    with pytest.raises(HTTPException) as exc:
        update_loan(session, "missing", LoanUpdate(loan_name="x"))
    assert exc.value.status_code == 404


def test_update_loan_ignores_repayed(session: Session):
    create_loan(session, _loan())
    create_loan_detail(session, "LN-001", _detail(price=100_000))
    # client tries to override repayed
    update_loan(session, "LN-001", LoanUpdate(repayed=999.0))
    row = session.get(Loan, "LN-001")
    assert row.repayed == 100_000  # still server-computed


def test_delete_loan_service(session: Session):
    create_loan(session, _loan())
    delete_loan(session, "LN-001")
    assert session.get(Loan, "LN-001") is None


def test_recalculate_repayed_helper(session: Session):
    create_loan(session, _loan())
    create_loan_detail(session, "LN-001", _detail(excute_type="principal", price=100))
    create_loan_detail(session, "LN-001", _detail(excute_type="interest", price=50))
    _recalculate_repayed(session, "LN-001")
    assert session.get(Loan, "LN-001").repayed == 100


def test_list_loan_details_service(session: Session):
    create_loan(session, _loan())
    create_loan_detail(session, "LN-001", _detail())
    rows = list_loan_details(session, "LN-001")
    assert len(rows) == 1


def test_create_loan_detail_updates_repayed(session: Session):
    create_loan(session, _loan())
    create_loan_detail(session, "LN-001", _detail(price=12345))
    assert session.get(Loan, "LN-001").repayed == 12345


def test_update_loan_detail_404(session: Session):
    with pytest.raises(HTTPException) as exc:
        update_loan_detail(session, 9999, LoanJournalUpdate(memo="x"))
    assert exc.value.status_code == 404


def test_delete_loan_detail_decrements_repayed(session: Session):
    create_loan(session, _loan())
    d = create_loan_detail(session, "LN-001", _detail(price=100))
    create_loan_detail(session, "LN-001", _detail(price=200))
    delete_loan_detail(session, d.distinct_number)
    assert session.get(Loan, "LN-001").repayed == 200


def test_get_loans_happy(client: TestClient, session: Session):
    create_loan(session, _loan())
    resp = client.get("/assets/loans")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1


def test_loan_selection_happy(client: TestClient, session: Session):
    create_loan(session, _loan())
    resp = client.get("/assets/loans/selection")
    assert resp.status_code == 200
    assert resp.json()["data"][0]["loan_id"] == "LN-001"


def test_get_loan_404_endpoint(client: TestClient):
    resp = client.get("/assets/loans/missing")
    assert resp.status_code == 404


def test_post_loan_happy(client: TestClient):
    resp = client.post("/assets/loans", json=_loan().model_dump())
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["apply_date"] == "20230601"


def test_put_loan_404(client: TestClient):
    resp = client.put("/assets/loans/missing", json={"loan_name": "x"})
    assert resp.status_code == 404


def test_delete_loan_happy(client: TestClient, session: Session):
    create_loan(session, _loan())
    resp = client.delete("/assets/loans/LN-001")
    assert resp.status_code == 200


def test_get_loan_details_happy(client: TestClient, session: Session):
    create_loan(session, _loan())
    create_loan_detail(session, "LN-001", _detail())
    resp = client.get("/assets/loans/LN-001/details")
    assert resp.status_code == 200


def test_post_loan_detail_422_invalid_type(client: TestClient, session: Session):
    create_loan(session, _loan())
    payload = _detail().model_dump()
    payload["loan_excute_type"] = "bogus"
    resp = client.post("/assets/loans/LN-001/details", json=payload)
    assert resp.status_code == 422


def test_put_loan_detail_404(client: TestClient):
    resp = client.put("/assets/loans/details/9999", json={"memo": "x"})
    assert resp.status_code == 404


def test_delete_loan_detail_happy(client: TestClient, session: Session):
    create_loan(session, _loan())
    d = create_loan_detail(session, "LN-001", _detail())
    resp = client.delete(f"/assets/loans/details/{d.distinct_number}")
    assert resp.status_code == 200


def test_router_mounted(client: TestClient):
    resp = client.get("/assets/loans")
    assert resp.status_code == 200


def test_loan_repayed_golden(client: TestClient, session: Session):
    create_loan(session, _loan())
    # 3 principal (100k, 200k, 50k) + 1 interest (5k) + 1 fee (2k)
    payloads = [
        ("principal", 100_000),
        ("principal", 200_000),
        ("principal", 50_000),
        ("interest", 5_000),
        ("fee", 2_000),
    ]
    detail_ids = []
    for excute_type, price in payloads:
        d = LoanJournalCreate(
            loan_id="LN-001",
            loan_excute_type=excute_type,
            excute_price=price,
            excute_date="2024-03-01",
        )
        resp = client.post("/assets/loans/LN-001/details", json=d.model_dump())
        assert resp.status_code == 200, resp.text
        detail_ids.append(resp.json()["data"]["distinct_number"])

    session.expire_all()
    assert session.get(Loan, "LN-001").repayed == 350_000

    # Delete the 200k principal row (index 1)
    resp = client.delete(f"/assets/loans/details/{detail_ids[1]}")
    assert resp.status_code == 200
    session.expire_all()
    assert session.get(Loan, "LN-001").repayed == 150_000

    # Update the 100k principal row (index 0) to 120k
    resp = client.put(
        f"/assets/loans/details/{detail_ids[0]}",
        json={"excute_price": 120_000},
    )
    assert resp.status_code == 200
    session.expire_all()
    assert session.get(Loan, "LN-001").repayed == 170_000
