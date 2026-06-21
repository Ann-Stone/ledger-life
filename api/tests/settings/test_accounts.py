"""BE-010 — Account CRUD tests."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.settings.account import (
    Account,
    AccountCreate,
    AccountRead,
    AccountUpdate,
)
from app.services.setting_service import (
    create_account,
    delete_account,
    list_accounts,
    list_accounts_selection,
    update_account,
)


def _make_payload(**overrides) -> dict:
    base = {
        "account_id": "BANK-CHASE-01",
        "name": "Chase Checking",
        "account_type": "bank",
        "fx_code": "USD",
        "is_calculate": "Y",
        "in_use": "Y",
        "discount": 1.0,
        "memo": "Primary checking",
        "owner": "stone",
    }
    base.update(overrides)
    return base


def test_schema_examples() -> None:
    for cls in (Account, AccountCreate, AccountUpdate, AccountRead):
        js = cls.model_json_schema()
        assert "example" in js, cls.__name__
        for n, p in js["properties"].items():
            assert "description" in p, f"{cls.__name__}.{n}"
            assert "examples" in p, f"{cls.__name__}.{n}"


# ---- service layer ----


def test_list_service(session: Session) -> None:
    create_account(session, AccountCreate(**_make_payload(account_id="A1", name="Bank A")))
    create_account(session, AccountCreate(**_make_payload(account_id="A2", name="Wallet B", account_type="cash")))
    assert len(list_accounts(session)) == 2
    assert len(list_accounts(session, name="Bank")) == 1
    assert len(list_accounts(session, account_type="cash")) == 1
    assert len(list_accounts(session, in_use="Y")) == 2


def test_selection_ordering(session: Session) -> None:
    create_account(session, AccountCreate(**_make_payload(account_id="A1", name="A1", account_index=3)))
    create_account(session, AccountCreate(**_make_payload(account_id="A2", name="A2", account_index=1)))
    create_account(session, AccountCreate(**_make_payload(account_id="A3", name="A3", account_index=2, in_use="N")))
    rows = list_accounts_selection(session)
    assert [r.account_id for r in rows] == ["A2", "A1"]


def test_create_autofills_index(session: Session) -> None:
    a1 = create_account(session, AccountCreate(**_make_payload(account_id="A1", name="A1")))
    assert a1.account_index == 1
    a2 = create_account(session, AccountCreate(**_make_payload(account_id="A2", name="A2")))
    assert a2.account_index == 2
    a3 = create_account(session, AccountCreate(**_make_payload(account_id="A3", name="A3", account_index=99)))
    assert a3.account_index == 99


def test_update_404(session: Session) -> None:
    import pytest
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as ei:
        update_account(session, 999, AccountUpdate(name="x"))
    assert ei.value.status_code == 404


def test_delete_404(session: Session) -> None:
    import pytest
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as ei:
        delete_account(session, 999)
    assert ei.value.status_code == 404


# ---- router / endpoint layer ----


def test_router_mounted(client: TestClient) -> None:
    paths = set(client.app.openapi()["paths"].keys())
    assert "/settings/accounts" in paths
    assert "/settings/accounts/selection" in paths
    assert "/settings/accounts/{id}" in paths


def test_get_list_happy(client: TestClient, session: Session) -> None:
    create_account(session, AccountCreate(**_make_payload(account_id="A1", name="A1")))
    res = client.get("/settings/accounts")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == 1
    assert len(body["data"]) == 1
    assert body["data"][0]["account_id"] == "A1"


def test_selection_endpoint(client: TestClient, session: Session) -> None:
    create_account(session, AccountCreate(**_make_payload(account_id="A1", name="A1", account_index=5)))
    create_account(session, AccountCreate(**_make_payload(account_id="A2", name="A2", account_index=2)))
    res = client.get("/settings/accounts/selection")
    assert res.status_code == 200
    data = res.json()["data"]
    assert [d["account_id"] for d in data] == ["A2", "A1"]


def test_post_happy(client: TestClient, session: Session) -> None:
    res = client.post("/settings/accounts", json=_make_payload())
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == 1
    assert body["data"]["account_id"] == "BANK-CHASE-01"
    assert body["data"]["account_index"] == 1
    assert session.exec(select(Account)).one().account_id == "BANK-CHASE-01"


def test_post_missing_account_id_returns_422(client: TestClient) -> None:
    payload = _make_payload()
    payload.pop("account_id")
    res = client.post("/settings/accounts", json=payload)
    assert res.status_code == 422


def test_post_duplicate_account_id_returns_409(client: TestClient, session: Session) -> None:
    create_account(session, AccountCreate(**_make_payload(account_id="DUP", name="x")))
    res = client.post("/settings/accounts", json=_make_payload(account_id="DUP", name="y"))
    assert res.status_code == 409


def test_put_happy(client: TestClient, session: Session) -> None:
    a = create_account(session, AccountCreate(**_make_payload(account_id="A1", name="orig")))
    res = client.put(f"/settings/accounts/{a.id}", json={"name": "renamed", "in_use": "N"})
    assert res.status_code == 200
    assert res.json()["data"]["name"] == "renamed"
    assert res.json()["data"]["in_use"] == "N"


def test_put_unknown_id_returns_404(client: TestClient) -> None:
    res = client.put("/settings/accounts/999", json={"name": "x"})
    assert res.status_code == 404


def test_delete_happy(client: TestClient, session: Session) -> None:
    a = create_account(session, AccountCreate(**_make_payload(account_id="A1", name="x")))
    res = client.delete(f"/settings/accounts/{a.id}")
    assert res.status_code == 200
    assert session.exec(select(Account)).all() == []


def test_delete_unknown_id_returns_404(client: TestClient) -> None:
    res = client.delete("/settings/accounts/999")
    assert res.status_code == 404
