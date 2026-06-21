"""BE-011 — Code / Sub-Code CRUD tests."""
from __future__ import annotations

from datetime import date

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.settings.budget import Budget
from app.models.settings.code_data import (
    CodeData,
    CodeDataCreate,
    CodeDataRead,
    CodeDataUpdate,
    CodeWithSubs,
)
from app.services.setting_service import (
    create_main_code,
    create_sub_code,
    delete_main_code,
    delete_sub_code,
    list_codes_with_sub_codes,
    list_main_codes,
    list_sub_codes,
    update_main_code,
    update_sub_code,
)


def _main_payload(**overrides) -> dict:
    base = {
        "code_id": "E01",
        "code_type": "Floating",
        "name": "Food",
        "in_use": "Y",
    }
    base.update(overrides)
    return base


def _sub_payload(parent_id: str, **overrides) -> dict:
    base = {
        "code_id": "E0101",
        "code_type": "Floating",
        "name": "Lunch",
        "parent_id": parent_id,
        "in_use": "Y",
    }
    base.update(overrides)
    return base


def test_schema_examples() -> None:
    for cls in (CodeData, CodeDataCreate, CodeDataUpdate, CodeDataRead, CodeWithSubs):
        js = cls.model_json_schema()
        assert "example" in js
        for n, p in js["properties"].items():
            assert "description" in p, f"{cls.__name__}.{n}"
            assert "examples" in p, f"{cls.__name__}.{n}"


def test_all_with_sub_shape(session: Session) -> None:
    create_main_code(session, CodeDataCreate(**_main_payload(code_id="E01", name="Food")))
    create_sub_code(session, CodeDataCreate(**_sub_payload("E01", code_id="E0101", name="Lunch")))
    rows = list_codes_with_sub_codes(session)
    assert len(rows) == 1
    assert rows[0].code_id == "E01"
    assert len(rows[0].sub_codes) == 1
    assert rows[0].sub_codes[0].code_id == "E0101"


def test_is_annual_event_create_and_update(session: Session) -> None:
    create_main_code(
        session,
        CodeDataCreate(**_main_payload(code_id="EV1", name="LunarNY", is_annual_event=True)),
    )
    assert session.get(CodeData, "EV1").is_annual_event is True

    update_main_code(session, "EV1", CodeDataUpdate(is_annual_event=False))
    assert session.get(CodeData, "EV1").is_annual_event is False


def test_is_annual_event_defaults_false(session: Session) -> None:
    create_main_code(session, CodeDataCreate(**_main_payload(code_id="E02", name="Transit")))
    assert session.get(CodeData, "E02").is_annual_event is False


def test_list_main(session: Session) -> None:
    create_main_code(session, CodeDataCreate(**_main_payload(code_id="A", name="A", code_index=2)))
    create_main_code(session, CodeDataCreate(**_main_payload(code_id="B", name="B", code_index=1)))
    create_sub_code(session, CodeDataCreate(**_sub_payload("A", code_id="A1")))
    rows = list_main_codes(session)
    assert [r.code_id for r in rows] == ["B", "A"]


def test_all_with_sub_service(session: Session) -> None:
    create_main_code(session, CodeDataCreate(**_main_payload(code_id="E01")))
    create_sub_code(session, CodeDataCreate(**_sub_payload("E01", code_id="E0101")))
    create_sub_code(session, CodeDataCreate(**_sub_payload("E01", code_id="E0102", name="Coffee")))
    rows = list_codes_with_sub_codes(session)
    assert {s.code_id for s in rows[0].sub_codes} == {"E0101", "E0102"}


def test_create_main_auto_budget(session: Session) -> None:
    create_main_code(session, CodeDataCreate(**_main_payload(code_type="Fixed")))
    year = str(date.today().year)
    budget = session.exec(
        select(Budget).where(Budget.budget_year == year, Budget.category_code == "E01")
    ).one()
    assert all(getattr(budget, f"expected{m:02d}") == 0.0 for m in range(1, 13))


def test_update_main_404(session: Session) -> None:
    with pytest.raises(HTTPException) as ei:
        update_main_code(session, "MISSING", CodeDataUpdate(name="x"))
    assert ei.value.status_code == 404


def test_delete_main_404(session: Session) -> None:
    with pytest.raises(HTTPException) as ei:
        delete_main_code(session, "MISSING")
    assert ei.value.status_code == 404


def test_list_sub_under_parent(session: Session) -> None:
    create_main_code(session, CodeDataCreate(**_main_payload(code_id="E01")))
    create_sub_code(session, CodeDataCreate(**_sub_payload("E01", code_id="E0101")))
    rows = list_sub_codes(session, "E01")
    assert [r.code_id for r in rows] == ["E0101"]


def test_create_sub_parent_check(session: Session) -> None:
    with pytest.raises(HTTPException) as ei:
        create_sub_code(session, CodeDataCreate(**_sub_payload("MISSING")))
    assert ei.value.status_code == 404


def test_update_sub_404(session: Session) -> None:
    with pytest.raises(HTTPException) as ei:
        update_sub_code(session, "MISSING", CodeDataUpdate(name="x"))
    assert ei.value.status_code == 404


def test_delete_sub_404(session: Session) -> None:
    with pytest.raises(HTTPException) as ei:
        delete_sub_code(session, "MISSING")
    assert ei.value.status_code == 404


# ---- routers ----


def test_routers_mounted(client: TestClient) -> None:
    paths = set(client.app.openapi()["paths"].keys())
    assert {"/settings/codes", "/settings/codes/all-with-sub", "/settings/codes/{code_id}",
            "/settings/codes/{parent_id}/sub-codes", "/settings/sub-codes",
            "/settings/sub-codes/{code_id}"} <= paths


def test_get_codes_list(client: TestClient, session: Session) -> None:
    create_main_code(session, CodeDataCreate(**_main_payload()))
    res = client.get("/settings/codes")
    assert res.status_code == 200
    assert res.json()["data"][0]["code_id"] == "E01"


def test_all_with_sub_endpoint(client: TestClient, session: Session) -> None:
    create_main_code(session, CodeDataCreate(**_main_payload()))
    create_sub_code(session, CodeDataCreate(**_sub_payload("E01")))
    res = client.get("/settings/codes/all-with-sub")
    assert res.status_code == 200
    body = res.json()["data"]
    assert body[0]["sub_codes"][0]["code_id"] == "E0101"


def test_post_code_happy(client: TestClient) -> None:
    res = client.post("/settings/codes", json=_main_payload())
    assert res.status_code == 200
    assert res.json()["data"]["code_id"] == "E01"


def test_create_main_fixed_auto_budget(client: TestClient, session: Session) -> None:
    res = client.post("/settings/codes", json=_main_payload(code_type="Fixed"))
    assert res.status_code == 200
    year = str(date.today().year)
    budget = session.exec(
        select(Budget).where(Budget.budget_year == year, Budget.category_code == "E01")
    ).one()
    assert budget.expected01 == 0.0


def test_create_main_floating_auto_budget(client: TestClient, session: Session) -> None:
    client.post("/settings/codes", json=_main_payload(code_id="E02", code_type="Floating"))
    year = str(date.today().year)
    assert session.exec(
        select(Budget).where(Budget.budget_year == year, Budget.category_code == "E02")
    ).one()


def test_create_main_other_type_no_budget(client: TestClient, session: Session) -> None:
    client.post("/settings/codes", json=_main_payload(code_id="I01", code_type="Income"))
    year = str(date.today().year)
    rows = session.exec(
        select(Budget).where(Budget.budget_year == year, Budget.category_code == "I01")
    ).all()
    assert rows == []


def test_put_code_happy(client: TestClient, session: Session) -> None:
    create_main_code(session, CodeDataCreate(**_main_payload()))
    res = client.put("/settings/codes/E01", json={"name": "Food renamed"})
    assert res.status_code == 200
    assert res.json()["data"]["name"] == "Food renamed"


def test_delete_code_happy(client: TestClient, session: Session) -> None:
    create_main_code(session, CodeDataCreate(**_main_payload()))
    res = client.delete("/settings/codes/E01")
    assert res.status_code == 200


def test_sub_list_happy(client: TestClient, session: Session) -> None:
    create_main_code(session, CodeDataCreate(**_main_payload()))
    create_sub_code(session, CodeDataCreate(**_sub_payload("E01")))
    res = client.get("/settings/codes/E01/sub-codes")
    assert res.status_code == 200
    assert res.json()["data"][0]["code_id"] == "E0101"


def test_post_sub_happy(client: TestClient, session: Session) -> None:
    create_main_code(session, CodeDataCreate(**_main_payload()))
    res = client.post("/settings/sub-codes", json=_sub_payload("E01"))
    assert res.status_code == 200
    assert res.json()["data"]["parent_id"] == "E01"


def test_put_sub_happy(client: TestClient, session: Session) -> None:
    create_main_code(session, CodeDataCreate(**_main_payload()))
    create_sub_code(session, CodeDataCreate(**_sub_payload("E01")))
    res = client.put("/settings/sub-codes/E0101", json={"name": "Lunch renamed"})
    assert res.status_code == 200
    assert res.json()["data"]["name"] == "Lunch renamed"


def test_delete_sub_happy(client: TestClient, session: Session) -> None:
    create_main_code(session, CodeDataCreate(**_main_payload()))
    create_sub_code(session, CodeDataCreate(**_sub_payload("E01")))
    res = client.delete("/settings/sub-codes/E0101")
    assert res.status_code == 200


def test_post_missing_code_id_returns_422(client: TestClient) -> None:
    payload = _main_payload()
    payload.pop("code_id")
    res = client.post("/settings/codes", json=payload)
    assert res.status_code == 422


def test_post_sub_unknown_parent_returns_404(client: TestClient) -> None:
    res = client.post("/settings/sub-codes", json=_sub_payload("MISSING"))
    assert res.status_code == 404
