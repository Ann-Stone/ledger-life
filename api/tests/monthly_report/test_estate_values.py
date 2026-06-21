"""Real-estate market-value (估值) endpoint + settlement integration tests."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.assets.estate import Estate, EstateJournal
from app.models.assets.estate_value_history import EstateValueHistory
from app.models.monthly_report.estate_net_value_history import EstateNetValueHistory
from app.services.settlement_service import run_estate_step


def _estate(**ov) -> Estate:
    base = dict(
        estate_id="EST-1",
        estate_name="主要住所",
        estate_type="residential",
        estate_address="123",
        asset_id="AC-REAL",
        fx_code="TWD",
        obtain_date="20200101",
        loan_id=None,
        estate_status="live",
    )
    base.update(ov)
    return Estate(**base)


def test_list_returns_estate_with_null_when_unrecorded(
    client: TestClient, session: Session
) -> None:
    session.add(_estate())
    session.commit()

    r = client.get("/monthly-report/estate-values/202604")
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data) == 1
    assert data[0]["estate_id"] == "EST-1"
    assert data[0]["market_value"] is None
    assert data[0]["recorded"] is False


def test_upsert_then_list_reflects_value(client: TestClient, session: Session) -> None:
    session.add(_estate())
    session.commit()

    r = client.post(
        "/monthly-report/estate-values",
        json={"estate_id": "EST-1", "vesting_month": "202604", "market_value": 13800000.0},
    )
    assert r.status_code == 201

    got = client.get("/monthly-report/estate-values/202604").json()["data"][0]
    assert got["market_value"] == 13800000.0
    assert got["recorded"] is True

    r2 = client.post(
        "/monthly-report/estate-values",
        json={"estate_id": "EST-1", "vesting_month": "202604", "market_value": 14000000.0},
    )
    assert r2.status_code == 201
    assert client.get("/monthly-report/estate-values/202604").json()["data"][0][
        "market_value"
    ] == 14000000.0


def test_value_carries_forward_to_later_month(
    client: TestClient, session: Session
) -> None:
    session.add(_estate())
    session.commit()
    client.post(
        "/monthly-report/estate-values",
        json={"estate_id": "EST-1", "vesting_month": "202601", "market_value": 12000000.0},
    )

    got = client.get("/monthly-report/estate-values/202603").json()["data"][0]
    assert got["market_value"] == 12000000.0  # carried forward
    assert got["vesting_month"] == "202601"
    assert got["recorded"] is False


def test_upsert_unknown_estate_returns_404(client: TestClient) -> None:
    r = client.post(
        "/monthly-report/estate-values",
        json={"estate_id": "NOPE", "vesting_month": "202604", "market_value": 1.0},
    )
    assert r.status_code == 404


def test_settlement_uses_recorded_market_value(session: Session) -> None:
    session.add(_estate())
    session.add(
        EstateJournal(
            estate_id="EST-1", estate_excute_type="purchase",
            excute_price=10000000.0, excute_date="20200115",
        )
    )
    session.add(
        EstateValueHistory(
            estate_id="EST-1", vesting_month="202601", market_value=13800000.0
        )
    )
    session.commit()

    run_estate_step(session, "202603")
    session.commit()
    row = session.exec(select(EstateNetValueHistory)).first()
    assert row.cost == 10000000.0  # purchase cost
    assert row.market_value == 13800000.0  # recorded appraisal wins, carried forward


def test_settlement_falls_back_to_cost_without_record(session: Session) -> None:
    session.add(_estate())
    session.add(
        EstateJournal(
            estate_id="EST-1", estate_excute_type="purchase",
            excute_price=10000000.0, excute_date="20200115",
        )
    )
    session.commit()

    run_estate_step(session, "202603")
    session.commit()
    row = session.exec(select(EstateNetValueHistory)).first()
    assert row.market_value == 10000000.0  # defaults to cost (no appraisal)
