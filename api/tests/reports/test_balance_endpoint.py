"""BE-025 — balance sheet endpoint tests."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.monthly_report.account_balance import AccountBalance
from app.models.monthly_report.credit_card_balance import CreditCardBalance
from app.models.monthly_report.loan_balance import LoanBalance


def test_get_balance_happy(client: TestClient) -> None:
    r = client.get("/reports/balance")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == 1
    data = body["data"]
    assert data["net_worth"] == 0.0
    assert data["assets"]["accounts"] == []


def test_get_balance_golden(client: TestClient, session: Session) -> None:
    session.add(
        AccountBalance(
            vesting_month="202604",
            id="A1",
            name="TWD Bank",
            balance=100000.0,
            fx_code="TWD",
            fx_rate=1.0,
            is_calculate="Y",
        )
    )
    session.add(
        AccountBalance(
            vesting_month="202604",
            id="A2",
            name="USD Bank",
            balance=1000.0,
            fx_code="USD",
            fx_rate=32.0,
            is_calculate="Y",
        )
    )
    session.add(
        LoanBalance(
            vesting_month="202604",
            id="L1",
            name="Mortgage",
            balance=-200000.0,
            cost=0.0,
            fx_code="TWD",
            fx_rate=1.0,
        )
    )
    session.add(
        CreditCardBalance(
            vesting_month="202604",
            id="CC1",
            name="Visa",
            balance=-3000.0,
            fx_rate=1.0,
        )
    )
    session.commit()

    r = client.get("/reports/balance")
    assert r.status_code == 200
    data = r.json()["data"]
    # 100000 + 32000 - 200000 - 3000 = -71000
    assert data["net_worth"] == -71000.0
    assert {line["name"] for line in data["assets"]["accounts"]} == {"TWD Bank", "USD Bank"}
    assert data["liabilities"]["loans"][0]["amount"] == -200000.0
    # original_amount carries the pre-FX native figure
    accounts_by_name = {line["name"]: line for line in data["assets"]["accounts"]}
    assert accounts_by_name["USD Bank"]["amount"] == 32000.0
    assert accounts_by_name["USD Bank"]["original_amount"] == 1000.0
    assert accounts_by_name["TWD Bank"]["original_amount"] == 100000.0
    assert data["liabilities"]["loans"][0]["original_amount"] == -200000.0
