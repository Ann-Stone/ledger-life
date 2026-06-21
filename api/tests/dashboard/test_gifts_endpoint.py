"""BE-028 — gifts endpoint tests."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.monthly_report.journal import Journal
from app.models.settings.account import Account


def _account(account_id: str, owner: str, fx_code: str = "TWD") -> Account:
    return Account(
        account_id=account_id,
        name=f"acc-{account_id}",
        account_type="bank",
        fx_code=fx_code,
        is_calculate="Y",
        in_use="Y",
        discount=1.0,
        memo=None,
        owner=owner,
        account_index=1,
    )


def _transfer(spend_way: str, action_sub: str, spending: float, vesting_month: str = "202604", spend_date: str = "20260410") -> Journal:
    return Journal(
        vesting_month=vesting_month,
        spend_date=spend_date,
        spend_way=spend_way,
        spend_way_type="account",
        spend_way_table="Account",
        action_main="Transfer",
        action_main_type="transfer",
        action_main_table="Code_Data",
        action_sub=action_sub,
        action_sub_type="account",
        action_sub_table="Account",
        spending=spending,
    )


def test_get_gifts_happy(client: TestClient, session: Session) -> None:
    session.add(_account("ALICE-A", "Alice"))
    session.add(_account("BOB-A", "Bob"))
    session.add(_transfer("ALICE-A", "BOB-A", -1000.0))
    session.commit()

    r = client.get("/dashboard/gifts/2026")
    assert r.status_code == 200
    items = r.json()["data"]
    assert len(items) == 1
    assert items[0]["owner"] == "Alice"
    assert items[0]["amount"] == 1000.0
    assert items[0]["rate"] == round(1000.0 * 100 / 2_200_000, 2)


def test_get_gifts_excludes_same_owner(client: TestClient, session: Session) -> None:
    session.add(_account("ALICE-A", "Alice"))
    session.add(_account("ALICE-B", "Alice"))
    session.add(_transfer("ALICE-A", "ALICE-B", -1000.0))
    session.commit()

    r = client.get("/dashboard/gifts/2026")
    assert r.json()["data"] == []


def test_get_gifts_invalid_year_returns_422(client: TestClient) -> None:
    r = client.get("/dashboard/gifts/26")
    assert r.status_code == 422
