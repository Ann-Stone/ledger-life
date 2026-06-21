"""BE-013 — Credit Card CRUD tests."""
from __future__ import annotations

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.settings.credit_card import (
    CreditCard,
    CreditCardCreate,
    CreditCardRead,
    CreditCardUpdate,
)
from app.services.setting_service import (
    create_credit_card,
    delete_credit_card,
    list_credit_cards,
    update_credit_card,
)


def _payload(**overrides) -> dict:
    base = {
        "credit_card_id": "CC-01",
        "card_name": "Chase Sapphire",
        "fx_code": "USD",
        "in_use": "Y",
    }
    base.update(overrides)
    return base


def test_schema_examples() -> None:
    for cls in (CreditCard, CreditCardCreate, CreditCardUpdate, CreditCardRead):
        js = cls.model_json_schema()
        assert "example" in js
        for n, p in js["properties"].items():
            assert "description" in p, f"{cls.__name__}.{n}"
            assert "examples" in p, f"{cls.__name__}.{n}"


def test_list_ordering(session: Session) -> None:
    create_credit_card(session, CreditCardCreate(**_payload(credit_card_id="A", credit_card_index=2)))
    create_credit_card(session, CreditCardCreate(**_payload(credit_card_id="B", credit_card_index=1)))
    rows = list_credit_cards(session)
    assert [r.credit_card_id for r in rows] == ["B", "A"]


def test_create_autofills_index(session: Session) -> None:
    a = create_credit_card(session, CreditCardCreate(**_payload(credit_card_id="A")))
    b = create_credit_card(session, CreditCardCreate(**_payload(credit_card_id="B")))
    assert a.credit_card_index == 1
    assert b.credit_card_index == 2


def test_update_404(session: Session) -> None:
    with pytest.raises(HTTPException) as ei:
        update_credit_card(session, "MISSING", CreditCardUpdate(card_name="x"))
    assert ei.value.status_code == 404


def test_delete_404(session: Session) -> None:
    with pytest.raises(HTTPException) as ei:
        delete_credit_card(session, "MISSING")
    assert ei.value.status_code == 404


def test_list_filters(session: Session) -> None:
    create_credit_card(session, CreditCardCreate(**_payload(credit_card_id="A", card_name="Cathay World", in_use="Y")))
    create_credit_card(session, CreditCardCreate(**_payload(credit_card_id="B", card_name="Chase", in_use="N")))
    assert [r.credit_card_id for r in list_credit_cards(session, card_name="Cathay")] == ["A"]
    assert [r.credit_card_id for r in list_credit_cards(session, in_use="N")] == ["B"]


# ---- routers ----


def test_router_mounted(client: TestClient) -> None:
    paths = set(client.app.openapi()["paths"].keys())
    assert {
        "/settings/credit-cards",
        "/settings/credit-cards/{credit_card_id}",
    } <= paths


def test_get_list_happy(client: TestClient, session: Session) -> None:
    create_credit_card(session, CreditCardCreate(**_payload()))
    res = client.get("/settings/credit-cards")
    assert res.status_code == 200
    assert res.json()["data"][0]["credit_card_id"] == "CC-01"


def test_post_happy(client: TestClient) -> None:
    res = client.post("/settings/credit-cards", json=_payload())
    assert res.status_code == 200
    body = res.json()["data"]
    assert body["credit_card_id"] == "CC-01"
    assert body["credit_card_index"] == 1


def test_post_missing_field_returns_422(client: TestClient) -> None:
    payload = _payload()
    payload.pop("card_name")
    res = client.post("/settings/credit-cards", json=payload)
    assert res.status_code == 422


def test_put_happy(client: TestClient, session: Session) -> None:
    create_credit_card(session, CreditCardCreate(**_payload()))
    res = client.put("/settings/credit-cards/CC-01", json={"card_name": "Renamed"})
    assert res.status_code == 200
    assert res.json()["data"]["card_name"] == "Renamed"


def test_put_unknown_id_returns_404(client: TestClient) -> None:
    res = client.put("/settings/credit-cards/MISSING", json={"card_name": "x"})
    assert res.status_code == 404


def test_delete_happy(client: TestClient, session: Session) -> None:
    create_credit_card(session, CreditCardCreate(**_payload()))
    res = client.delete("/settings/credit-cards/CC-01")
    assert res.status_code == 200


def test_delete_unknown_id_returns_404(client: TestClient) -> None:
    res = client.delete("/settings/credit-cards/MISSING")
    assert res.status_code == 404
