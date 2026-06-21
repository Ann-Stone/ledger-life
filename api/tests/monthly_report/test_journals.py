"""BE-016 — Journal CRUD tests."""
from __future__ import annotations

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.dashboard.fx_rate import FXRate
from app.models.monthly_report.journal import (
    Journal,
    JournalCreate,
    JournalMonthRead,
    JournalRead,
    JournalUpdate,
)
from app.models.settings.account import Account, AccountCreate
from app.services.monthly_report_service import (
    compute_gain_loss,
    create_journal,
    delete_journal,
    list_journals_by_month,
    normalize_spend_date,
    update_journal,
)
from app.services.setting_service import create_account


def _payload(**overrides) -> dict:
    base = {
        "vesting_month": "202604",
        "spend_date": "20260418",
        "spend_way": "BANK-01",
        "spend_way_type": "account",
        "spend_way_table": "Account",
        "action_main": "EXP01",
        "action_main_type": "expense",
        "action_main_table": "Code_Data",
        "action_sub": None,
        "action_sub_type": None,
        "action_sub_table": None,
        "spending": -100.0,
        "invoice_number": None,
        "note": "Lunch",
    }
    base.update(overrides)
    return base


# ---- Sub-task 1: schema docs ----


def test_journal_schema_examples() -> None:
    for cls in (Journal, JournalCreate, JournalUpdate, JournalRead):
        js = cls.model_json_schema()
        assert "example" in js, cls.__name__
        for n, p in js["properties"].items():
            assert "description" in p, f"{cls.__name__}.{n}"
            assert "examples" in p, f"{cls.__name__}.{n}"


# ---- Sub-task 2: JournalMonthRead ----


def test_journal_month_read_example() -> None:
    js = JournalMonthRead.model_json_schema()
    assert "example" in js
    example = js["example"]
    assert "items" in example and "gain_loss" in example


# ---- Sub-task 3: normalize_spend_date ----


def test_normalize_spend_date() -> None:
    assert normalize_spend_date("20260418") == "20260418"
    assert normalize_spend_date("2026-04-18T00:00:00.000Z") == "20260418"
    assert normalize_spend_date("2026-04-18T12:34:56") == "20260418"
    with pytest.raises(ValueError):
        normalize_spend_date("not-a-date")
    with pytest.raises(ValueError):
        normalize_spend_date("20261301")
    with pytest.raises(ValueError):
        normalize_spend_date("")


# ---- Sub-task 4: list_journals_by_month ----


def test_list_journals_by_month(session: Session) -> None:
    create_journal(session, JournalCreate(**_payload(spend_date="20260420", spending=-50.0)))
    create_journal(session, JournalCreate(**_payload(spend_date="20260415", spending=-30.0)))
    create_journal(session, JournalCreate(**_payload(vesting_month="202605", spending=-99.0)))

    rows = list_journals_by_month(session, "202604")
    assert len(rows) == 2
    assert [r.spend_date for r in rows] == ["20260415", "20260420"]


# ---- Sub-task 5: compute_gain_loss golden ----


def _account_payload(**overrides) -> dict:
    base = {
        "account_id": "BANK-01",
        "name": "TWD Bank",
        "account_type": "bank",
        "fx_code": "TWD",
        "is_calculate": "Y",
        "in_use": "Y",
        "discount": 1.0,
        "memo": None,
        "owner": "stone",
    }
    base.update(overrides)
    return base


def test_compute_gain_loss_golden(session: Session) -> None:
    twd = create_account(session, AccountCreate(**_account_payload(account_id="BANK-01", fx_code="TWD")))
    usd = create_account(session, AccountCreate(**_account_payload(account_id="BANK-USD", name="USD Bank", fx_code="USD")))
    session.add(FXRate(import_date="20260430", code="USD", buy_rate=32.0))
    session.commit()

    # spend_way references the account by PK (Account.id), not account_id.
    create_journal(session, JournalCreate(**_payload(spend_way=str(twd.id), spending=200.0)))
    create_journal(session, JournalCreate(**_payload(spend_way=str(twd.id), spending=-50.0)))
    create_journal(session, JournalCreate(**_payload(spend_way=str(usd.id), spending=10.0)))

    journals = list_journals_by_month(session, "202604")
    # 200 - 50 + 10*32 = 470
    assert compute_gain_loss(session, journals) == 470.0


def test_compute_gain_loss_empty(session: Session) -> None:
    assert compute_gain_loss(session, []) == 0.0


# ---- Sub-task 6: create autoincrement ----


def test_create_journal_autoincrement(session: Session) -> None:
    j1 = create_journal(session, JournalCreate(**_payload()))
    j2 = create_journal(session, JournalCreate(**_payload()))
    assert j1.distinct_number is not None
    assert j2.distinct_number is not None
    assert j2.distinct_number == j1.distinct_number + 1


def test_create_journal_normalizes_iso(session: Session) -> None:
    row = create_journal(
        session,
        JournalCreate(**_payload(spend_date="2026-04-18T00:00:00.000Z")),
    )
    assert row.spend_date == "20260418"


# ---- Sub-task 7: update ----


def test_update_journal_not_found(session: Session) -> None:
    with pytest.raises(HTTPException) as ei:
        update_journal(session, 999, JournalUpdate(note="x"))
    assert ei.value.status_code == 404


def test_update_journal_normalizes_spend_date(session: Session) -> None:
    j = create_journal(session, JournalCreate(**_payload()))
    updated = update_journal(
        session,
        j.distinct_number,
        JournalUpdate(spend_date="2026-04-19T00:00:00Z"),
    )
    assert updated.spend_date == "20260419"


# ---- Sub-task 8: delete ----


def test_delete_journal_not_found(session: Session) -> None:
    with pytest.raises(HTTPException) as ei:
        delete_journal(session, 999)
    assert ei.value.status_code == 404


# ---- Sub-task 9: GET endpoint ----


def test_get_journals_by_month_endpoint(client: TestClient, session: Session) -> None:
    create_account(session, AccountCreate(**_account_payload()))
    create_journal(session, JournalCreate(**_payload()))

    r = client.get("/monthly-report/journals/202604")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == 1
    data = body["data"]
    assert len(data["items"]) == 1
    assert data["gain_loss"] == -100.0


# ---- Sub-task 10: POST 201 ----


def test_post_journal_created(client: TestClient) -> None:
    r = client.post("/monthly-report/journals", json=_payload())
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == 1
    assert body["data"]["distinct_number"] >= 1


# ---- Sub-task 11: PUT 404 ----


def test_put_journal_not_found(client: TestClient) -> None:
    r = client.put("/monthly-report/journals/9999", json={"note": "x"})
    assert r.status_code == 404


def test_put_journal_success(client: TestClient) -> None:
    cr = client.post("/monthly-report/journals", json=_payload()).json()
    jid = cr["data"]["distinct_number"]
    r = client.put(f"/monthly-report/journals/{jid}", json={"note": "Updated"})
    assert r.status_code == 200
    assert r.json()["data"]["note"] == "Updated"


# ---- Sub-task 12: DELETE ----


def test_delete_journal_success(client: TestClient, session: Session) -> None:
    j = create_journal(session, JournalCreate(**_payload()))
    r = client.delete(f"/monthly-report/journals/{j.distinct_number}")
    assert r.status_code == 200
    assert r.json()["data"] == {"deleted": j.distinct_number}
    assert session.exec(select(Journal)).first() is None


def test_delete_journal_endpoint_not_found(client: TestClient) -> None:
    r = client.delete("/monthly-report/journals/9999")
    assert r.status_code == 404


# ---- Sub-task 13: router mounted ----


def test_router_mounted() -> None:
    from app.main import app

    # Use FastAPI's own resolved schema paths rather than walking app.routes:
    # the internal route-tree structure changed across starlette versions, but
    # openapi()["paths"] is the stable, version-agnostic view of mounted paths.
    paths = set(app.openapi()["paths"])
    assert "/monthly-report/journals/{vesting_month}" in paths
    assert "/monthly-report/journals" in paths
    assert "/monthly-report/journals/{journal_id}" in paths
