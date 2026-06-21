"""Router-level tests for /utilities/selections/* endpoints."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.assets.other_asset import OtherAsset
from app.models.assets.stock import StockJournal
from app.models.assets.stock_category import StockCategory
from app.models.settings.account import Account
from app.models.settings.code_data import CodeData


def _seed_account(session: Session) -> None:
    session.add(
        Account(
            account_id="AC1",
            name="Cash NTD",
            account_type="CASH",
            fx_code="TWD",
            is_calculate="Y",
            in_use="Y",
            discount=1.0,
            owner=None,
            memo=None,
            account_index=1,
        )
    )
    session.commit()


def test_all_selection_endpoints_return_envelope(client: TestClient, session: Session) -> None:
    for path in (
        "/utilities/selections/accounts",
        "/utilities/selections/credit-cards",
        "/utilities/selections/loans",
        "/utilities/selections/insurances",
        "/utilities/selections/other-asset-types",
        "/utilities/selections/stocks",
        "/utilities/selections/stock-categories",
        "/utilities/selections/codes",
    ):
        resp = client.get(path)
        assert resp.status_code == 200, path
        body = resp.json()
        assert body["status"] == 1, path
        assert isinstance(body["data"], list), path


def test_account_selection_groups_happy(client: TestClient, session: Session) -> None:
    _seed_account(session)
    resp = client.get("/utilities/selections/accounts")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == 1
    assert body["data"][0]["label"] == "CASH"
    assert body["data"][0]["options"][0]["label"] == "Cash NTD"
    # Value is the account PK (Account.id) stringified — Journal.spend_way
    # references the account by primary key, symmetric with credit cards.
    account_id = session.exec(select(Account)).one().id
    assert body["data"][0]["options"][0]["value"] == str(account_id)


def test_stock_selection_grouped_by_asset_id(client: TestClient, session: Session) -> None:
    session.add(
        StockJournal(
            stock_id="STK-H-001",
            stock_code="AAPL",
            stock_name="Apple Inc.",
            asset_id="AC-STK-001",
            expected_spend=10000.0,
        )
    )
    session.add(
        StockJournal(
            stock_id="STK-H-002",
            stock_code="TSLA",
            stock_name="Tesla",
            asset_id="AC-STK-002",
            expected_spend=5000.0,
        )
    )
    session.commit()

    resp = client.get("/utilities/selections/stocks")
    assert resp.status_code == 200
    groups = resp.json()["data"]
    labels = {g["label"] for g in groups}
    assert labels == {"AC-STK-001", "AC-STK-002"}
    first = next(g for g in groups if g["label"] == "AC-STK-001")
    assert first["options"][0]["value"] == "STK-H-001"
    assert first["options"][0]["label"] == "AAPL Apple Inc."


def test_other_asset_type_selection_distinct(
    client: TestClient, session: Session
) -> None:
    session.add(
        OtherAsset(
            asset_id="AC-STK-001",
            asset_name="US equities",
            asset_type="stock",
            in_use="Y",
            asset_index=1,
        )
    )
    session.add(
        OtherAsset(
            asset_id="AC-STK-002",
            asset_name="TW equities",
            asset_type="stock",
            in_use="Y",
            asset_index=2,
        )
    )
    session.add(
        OtherAsset(
            asset_id="AC-INS-001",
            asset_name="Term life",
            asset_type="insurance",
            in_use="Y",
            asset_index=3,
        )
    )
    session.add(
        OtherAsset(
            asset_id="AC-EST-IGN",
            asset_name="Old land",
            asset_type="estate",
            in_use="N",  # filtered out
            asset_index=4,
        )
    )
    session.commit()

    resp = client.get("/utilities/selections/other-asset-types")
    assert resp.status_code == 200
    groups = resp.json()["data"]
    assert len(groups) == 1
    assert groups[0]["label"] == "Other_Asset"
    values = [o["value"] for o in groups[0]["options"]]
    # stock appears once even though two rows have it; estate excluded (in_use=N).
    assert values == ["stock", "insurance"]


def test_stock_category_selection_happy(client: TestClient, session: Session) -> None:
    session.add(StockCategory(category_id="SC-001", name="成長型", in_use="Y", category_index=1))
    session.add(StockCategory(category_id="SC-002", name="債券", in_use="N", category_index=2))
    session.commit()

    resp = client.get("/utilities/selections/stock-categories")
    assert resp.status_code == 200
    groups = resp.json()["data"]
    assert len(groups) == 1
    assert groups[0]["label"] == "Stock_Category"
    # in_use="N" category is excluded from the dropdown.
    values = [o["value"] for o in groups[0]["options"]]
    assert values == ["SC-001"]
    assert groups[0]["options"][0]["label"] == "成長型"


def test_credit_card_selection_empty(client: TestClient, session: Session) -> None:
    resp = client.get("/utilities/selections/credit-cards")
    assert resp.status_code == 200
    assert resp.json()["data"] == []


def test_sub_code_group_not_found_returns_404(client: TestClient, session: Session) -> None:
    resp = client.get("/utilities/selections/codes/UNKNOWN")
    assert resp.status_code == 404
    body = resp.json()
    assert body["status"] == 0


def test_sub_code_group_happy(client: TestClient, session: Session) -> None:
    session.add(
        CodeData(
            code_id="MAIN-A",
            code_type="Floating",
            name="Food",
            parent_id=None,
            in_use="Y",
            code_index=1,
        )
    )
    session.add(
        CodeData(
            code_id="SUB-1",
            code_type="Floating",
            name="Groceries",
            parent_id="MAIN-A",
            in_use="Y",
            code_index=2,
        )
    )
    session.commit()

    resp = client.get("/utilities/selections/codes/MAIN-A")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == 1
    assert body["data"][0]["label"] == "sub"
    assert body["data"][0]["options"][0]["value"] == "SUB-1"
