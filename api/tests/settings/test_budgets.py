"""BE-012 — Budget generation (suggest), apply (upsert), and endpoint tests."""
from __future__ import annotations

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.monthly_report.journal import Journal
from app.models.settings.budget import Budget, BudgetCreate, BudgetRead, BudgetUpdate
from app.models.settings.code_data import CodeData
from app.services.setting_service import (
    apply_budget,
    bulk_update_budgets,
    list_budget_year_range,
    list_budgets_by_year,
    suggest_budget,
)


def _zero_months() -> dict[str, float]:
    return {f"expected{m:02d}": 0.0 for m in range(1, 13)}


def _seed_budget(session: Session, year: str, code: str, **months) -> Budget:
    payload = _zero_months()
    payload.update(months)
    b = Budget(
        budget_year=year,
        category_code=code,
        category_name=code,
        code_type="Floating",
        **payload,
    )
    session.add(b)
    session.commit()
    session.refresh(b)
    return b


def _budget_create(year: str, code: str, **fields) -> BudgetCreate:
    payload = _zero_months()
    payload.update(fields)
    return BudgetCreate(
        budget_year=year,
        category_code=code,
        category_name=code,
        code_type="Floating",
        **payload,
    )


def _seed_code(
    session: Session,
    code_id: str,
    name: str = "X",
    code_type: str = "Floating",
    *,
    is_annual_event: bool = False,
) -> CodeData:
    c = CodeData(
        code_id=code_id,
        code_type=code_type,
        name=name,
        in_use="Y",
        code_index=1,
        is_annual_event=is_annual_event,
    )
    session.add(c)
    session.commit()
    session.refresh(c)
    return c


def _seed_journal(
    session: Session,
    spend_date: str,
    action_main: str,
    spending: float,
    action_main_type: str = "Floating",
) -> None:
    j = Journal(
        vesting_month=spend_date[:6],
        spend_date=spend_date,
        spend_way="A",
        spend_way_type="account",
        spend_way_table="Account",
        action_main=action_main,
        action_main_type=action_main_type,
        action_main_table="Code_Data",
        spending=spending,
    )
    session.add(j)
    session.commit()


def test_schema_examples() -> None:
    for cls in (Budget, BudgetCreate, BudgetUpdate, BudgetRead):
        js = cls.model_json_schema()
        assert "example" in js
        for n, p in js["properties"].items():
            assert "description" in p, f"{cls.__name__}.{n}"
            assert "examples" in p, f"{cls.__name__}.{n}"


def test_list_by_year(session: Session) -> None:
    _seed_budget(session, "2026", "B")
    _seed_budget(session, "2026", "A")
    _seed_budget(session, "2025", "C")
    rows = list_budgets_by_year(session, 2026)
    assert [r.category_code for r in rows] == ["A", "B"]


def test_year_range_distinct(session: Session) -> None:
    _seed_budget(session, "2024", "A")
    _seed_budget(session, "2026", "A")
    _seed_budget(session, "2025", "A")
    assert list_budget_year_range(session) == [2024, 2025, 2026]


def test_bulk_update_partial(session: Session) -> None:
    _seed_budget(session, "2026", "A")
    _seed_budget(session, "2026", "B")
    rows = bulk_update_budgets(
        session,
        [
            BudgetUpdate(budget_year="2026", category_code="A", expected01=100.0),
            BudgetUpdate(budget_year="2026", category_code="B", expected12=200.0),
        ],
    )
    assert len(rows) == 2
    assert rows[0].expected01 == 100.0
    assert rows[1].expected12 == 200.0


def test_bulk_update_404_rolls_back(session: Session) -> None:
    _seed_budget(session, "2026", "A")
    with pytest.raises(HTTPException) as ei:
        bulk_update_budgets(
            session,
            [
                BudgetUpdate(budget_year="2026", category_code="A", expected01=999.0),
                BudgetUpdate(budget_year="2026", category_code="MISSING", expected01=1.0),
            ],
        )
    assert ei.value.status_code == 404
    refreshed = session.get(Budget, ("2026", "A"))
    assert refreshed.expected01 == 0.0


# ---- suggest (robust seasonal + annual-event envelope) ----


def test_suggest_per_month_median_damps_one_off(session: Session) -> None:
    _seed_code(session, "E01", "Food", "Floating")
    # May spends 100 / 100 / 300 over three years -> median 100 (the 2025 spike is damped).
    _seed_journal(session, "20230515", "E01", -100.0)
    _seed_journal(session, "20240515", "E01", -100.0)
    _seed_journal(session, "20250515", "E01", -300.0)
    rows = suggest_budget(session, 2026)
    assert len(rows) == 1
    row = rows[0]
    assert row.category_code == "E01"
    assert row.annual_amount is None
    assert row.expected05 == 100.0
    assert row.expected01 == 0.0
    # suggest does not persist
    assert list_budgets_by_year(session, 2026) == []


def test_suggest_keyed_by_code_id_not_type(session: Session) -> None:
    _seed_code(session, "E01", "Food", "Floating")
    _seed_code(session, "E02", "Transit", "Floating")
    _seed_journal(session, "20250115", "E01", -100.0)
    _seed_journal(session, "20250115", "E02", -200.0)
    by_code = {r.category_code: r for r in suggest_budget(session, 2026)}
    assert set(by_code) == {"E01", "E02"}
    assert by_code["E01"].expected01 == 100.0
    assert by_code["E02"].expected01 == 200.0


def test_suggest_event_annual_envelope(session: Session) -> None:
    _seed_code(session, "EV1", "Lunar NY", "Floating", is_annual_event=True)
    # Annual totals 400 / 500 / 600 -> median 500; the spend month shifts Jan<->Feb across years.
    _seed_journal(session, "20230122", "EV1", -400.0)
    _seed_journal(session, "20240210", "EV1", -500.0)
    _seed_journal(session, "20250129", "EV1", -600.0)
    rows = suggest_budget(session, 2026)
    assert len(rows) == 1
    row = rows[0]
    assert row.annual_amount == 500.0
    assert all(getattr(row, f"expected{m:02d}") == 0.0 for m in range(1, 13))


def test_suggest_excludes_transfer_and_invest(session: Session) -> None:
    _seed_code(session, "E01", "Food", "Floating")
    _seed_code(session, "T01", "Transfer", "Transfer")
    _seed_code(session, "I01", "Invest", "Invest")
    _seed_journal(session, "20250115", "E01", -120.0)
    _seed_journal(session, "20250115", "T01", -9999.0, action_main_type="Transfer")
    _seed_journal(session, "20250115", "I01", -9999.0, action_main_type="Invest")
    rows = suggest_budget(session, 2026)
    assert {r.category_code for r in rows} == {"E01"}


# ---- apply (upsert) ----


def test_apply_inserts_then_updates(session: Session) -> None:
    apply_budget(session, [_budget_create("2026", "E01", expected01=100.0)])
    assert session.get(Budget, ("2026", "E01")).expected01 == 100.0
    apply_budget(session, [_budget_create("2026", "E01", expected01=250.0)])
    assert session.get(Budget, ("2026", "E01")).expected01 == 250.0


def test_apply_persists_annual_amount(session: Session) -> None:
    item = _budget_create("2026", "EV1")
    item.annual_amount = 12345.0
    rows = apply_budget(session, [item])
    assert rows[0].annual_amount == 12345.0


# ---- routers ----


def test_router_mounted(client: TestClient) -> None:
    paths = set(client.app.openapi()["paths"].keys())
    assert {
        "/settings/budgets/year-range",
        "/settings/budgets/{year}",
        "/settings/budgets",
        "/settings/budgets/{year}/suggest",
        "/settings/budgets/{year}/apply",
    } <= paths


def test_year_range_endpoint(client: TestClient, session: Session) -> None:
    _seed_budget(session, "2025", "A")
    _seed_budget(session, "2026", "A")
    res = client.get("/settings/budgets/year-range")
    assert res.status_code == 200
    assert res.json()["data"] == [2025, 2026]


def test_get_by_year_happy(client: TestClient, session: Session) -> None:
    _seed_budget(session, "2026", "A")
    res = client.get("/settings/budgets/2026")
    assert res.status_code == 200
    body = res.json()["data"]
    assert len(body) == 1 and body[0]["category_code"] == "A"


def test_get_by_year_invalid_422(client: TestClient) -> None:
    res = client.get("/settings/budgets/notayear")
    assert res.status_code == 422


def test_put_bulk_happy(client: TestClient, session: Session) -> None:
    _seed_budget(session, "2026", "A")
    res = client.put(
        "/settings/budgets",
        json=[{"budget_year": "2026", "category_code": "A", "expected03": 333.0}],
    )
    assert res.status_code == 200
    assert res.json()["data"][0]["expected03"] == 333.0


def test_put_bulk_404(client: TestClient) -> None:
    res = client.put(
        "/settings/budgets",
        json=[{"budget_year": "2099", "category_code": "Z", "expected01": 1.0}],
    )
    assert res.status_code == 404


def test_suggest_endpoint_does_not_persist(client: TestClient, session: Session) -> None:
    _seed_code(session, "E01", "Food", "Floating")
    _seed_journal(session, "20250115", "E01", -1200.0)
    res = client.post("/settings/budgets/2026/suggest")
    assert res.status_code == 200
    body = res.json()["data"]
    assert len(body) == 1
    assert body[0]["category_code"] == "E01"
    assert body[0]["expected01"] == 1200.0
    # nothing persisted by suggest
    assert client.get("/settings/budgets/2026").json()["data"] == []


def test_apply_endpoint_upserts(client: TestClient, session: Session) -> None:
    payload = [
        {
            "budget_year": "2026",
            "category_code": "E01",
            "category_name": "Food",
            "code_type": "Floating",
            **{f"expected{m:02d}": 0.0 for m in range(1, 13)},
            "expected01": 500.0,
        }
    ]
    res = client.post("/settings/budgets/2026/apply", json=payload)
    assert res.status_code == 200
    assert res.json()["data"][0]["expected01"] == 500.0
    got = client.get("/settings/budgets/2026").json()["data"]
    assert len(got) == 1 and got[0]["expected01"] == 500.0
