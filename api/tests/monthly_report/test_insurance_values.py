"""Insurance surrender-value (解約金) endpoint + settlement integration tests."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.assets.insurance import Insurance, InsuranceJournal
from app.models.assets.insurance_value_history import InsuranceValueHistory
from app.models.monthly_report.insurance_net_value_history import (
    InsuranceNetValueHistory,
)
from app.services.settlement_service import run_insurance_step


def _policy(**ov) -> Insurance:
    base = dict(
        insurance_id="INS-1",
        insurance_name="Whole life",
        asset_id="AC-INS",
        in_account="ACC-NONE",  # unknown account → base currency, rate 1.0
        out_account="ACC-NONE",
        start_date="20200101",
        end_date="20500101",
        pay_type="annual",
        pay_day="01/15",
        expected_spend=1200.0,
        has_closed="N",
    )
    base.update(ov)
    return Insurance(**base)


def test_list_returns_policy_with_null_when_unrecorded(
    client: TestClient, session: Session
) -> None:
    session.add(_policy())
    session.commit()

    r = client.get("/monthly-report/insurance-values/202604")
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data) == 1
    assert data[0]["insurance_id"] == "INS-1"
    assert data[0]["surrender_value"] is None
    assert data[0]["recorded"] is False


def test_upsert_then_list_reflects_value(client: TestClient, session: Session) -> None:
    session.add(_policy())
    session.commit()

    r = client.post(
        "/monthly-report/insurance-values",
        json={"insurance_id": "INS-1", "vesting_month": "202604", "surrender_value": 185000.0},
    )
    assert r.status_code == 201

    got = client.get("/monthly-report/insurance-values/202604").json()["data"][0]
    assert got["surrender_value"] == 185000.0
    assert got["vesting_month"] == "202604"
    assert got["recorded"] is True

    # Idempotent overwrite on the composite key.
    r2 = client.post(
        "/monthly-report/insurance-values",
        json={"insurance_id": "INS-1", "vesting_month": "202604", "surrender_value": 190000.0},
    )
    assert r2.status_code == 201
    assert client.get("/monthly-report/insurance-values/202604").json()["data"][0][
        "surrender_value"
    ] == 190000.0


def test_value_carries_forward_to_later_month(
    client: TestClient, session: Session
) -> None:
    session.add(_policy())
    session.commit()
    client.post(
        "/monthly-report/insurance-values",
        json={"insurance_id": "INS-1", "vesting_month": "202601", "surrender_value": 150000.0},
    )

    got = client.get("/monthly-report/insurance-values/202603").json()["data"][0]
    assert got["surrender_value"] == 150000.0  # carried forward
    assert got["vesting_month"] == "202601"
    assert got["recorded"] is False  # not recorded in 202603 itself


def test_upsert_unknown_policy_returns_404(client: TestClient) -> None:
    r = client.post(
        "/monthly-report/insurance-values",
        json={"insurance_id": "NOPE", "vesting_month": "202604", "surrender_value": 1.0},
    )
    assert r.status_code == 404


def test_settlement_uses_recorded_surrender_value(session: Session) -> None:
    session.add(_policy())
    session.add(
        InsuranceJournal(
            insurance_id="INS-1", insurance_excute_type="pay",
            excute_price=1200.0, excute_date="20260115",
        )
    )
    # Recorded 解約金 differs from premiums-paid (real cash value).
    session.add(
        InsuranceValueHistory(
            insurance_id="INS-1", vesting_month="202601", surrender_value=1500.0
        )
    )
    session.commit()

    run_insurance_step(session, "202603")
    session.commit()
    row = session.exec(select(InsuranceNetValueHistory)).first()
    assert row.cost == 1200.0  # premiums paid
    assert row.surrender_value == 1500.0  # recorded value wins, carried forward


def test_settlement_falls_back_to_premiums_without_record(session: Session) -> None:
    session.add(_policy())
    session.add(
        InsuranceJournal(
            insurance_id="INS-1", insurance_excute_type="pay",
            excute_price=1200.0, excute_date="20260115",
        )
    )
    session.commit()

    run_insurance_step(session, "202603")
    session.commit()
    row = session.exec(select(InsuranceNetValueHistory)).first()
    assert row.surrender_value == 1200.0  # net-premium estimate (no record)


def test_settlement_insurance_journal_type_semantics(session: Session) -> None:
    """pay adds to cost+surrender, cash reduces cost, return reduces
    surrender, expect is ignored entirely."""
    session.add(_policy())
    for excute_type, price, date in (
        ("pay", 1200.0, "20250115"),
        ("pay", 1200.0, "20260115"),
        ("cash", 100.0, "20260201"),
        ("return", 300.0, "20260210"),
        ("expect", 99999.0, "20260215"),
    ):
        session.add(
            InsuranceJournal(
                insurance_id="INS-1", insurance_excute_type=excute_type,
                excute_price=price, excute_date=date,
            )
        )
    session.commit()

    run_insurance_step(session, "202603")
    session.commit()
    row = session.exec(select(InsuranceNetValueHistory)).first()
    assert row.cost == 2300.0  # 1200 + 1200 - 100 (配息)
    assert row.surrender_value == 2100.0  # 1200 + 1200 - 300 (贖回)
