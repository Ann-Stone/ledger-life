"""House-price-index refresh + estate value suggestion tests (network mocked)."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.assets.estate import Estate, EstateJournal
from app.models.dashboard.house_price_index import HousePriceIndex
from app.services import house_price_index_service as svc

# INDEX_SOURCES pins 臺北市 → dataset 121969; that's the region refresh writes to.
REGION = "臺北市"


def _estate(**ov) -> Estate:
    base = dict(
        estate_id="EST-1", estate_name="主要住所", estate_type="residential",
        estate_address="123", asset_id="AC-REAL", fx_code="TWD",
        obtain_date="20200115", loan_id=None, estate_status="live", region=None,
    )
    base.update(ov)
    return Estate(**base)


def _purchase(price: float) -> EstateJournal:
    return EstateJournal(
        estate_id="EST-1", estate_excute_type="purchase",
        excute_price=price, excute_date="20200115",
    )


def test_roc_quarter_to_greg() -> None:
    assert svc.roc_quarter_to_greg("101Q3") == "2012Q3"   # ROC → Gregorian
    assert svc.roc_quarter_to_greg("113Q1") == "2024Q1"
    assert svc.roc_quarter_to_greg("2012Q3") == "2012Q3"  # already Gregorian
    assert svc.roc_quarter_to_greg("nope") is None


def test_refresh_index_upserts(session: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        svc, "_fetch_index_rows", lambda d, c: [("2020Q1", 100.0), ("2024Q1", 137.73)]
    )
    res = svc.refresh_index(session)
    assert res.ok is True
    assert res.upserted == 2
    rows = session.exec(select(HousePriceIndex)).all()
    assert {r.quarter for r in rows} == {"2020Q1", "2024Q1"}
    assert {r.region for r in rows} == {REGION}  # written under the configured region

    # Re-running upserts (idempotent), updating values not duplicating.
    monkeypatch.setattr(svc, "_fetch_index_rows", lambda d, c: [("2024Q1", 140.0)])
    svc.refresh_index(session)
    rows = session.exec(select(HousePriceIndex)).all()
    assert len(rows) == 2
    assert next(r.index_value for r in rows if r.quarter == "2024Q1") == 140.0


def test_refresh_index_best_effort_on_failure(
    session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    session.add(HousePriceIndex(region=REGION, quarter="2024Q1", index_value=137.0))
    session.commit()

    def boom(*_a):
        raise RuntimeError("network down")

    monkeypatch.setattr(svc, "_fetch_index_rows", boom)
    res = svc.refresh_index(session)
    assert res.ok is False
    assert res.upserted == 0
    # Existing data preserved.
    assert session.exec(select(HousePriceIndex)).first().index_value == 137.0


def test_suggest_uses_index_growth(session: Session) -> None:
    session.add(HousePriceIndex(region=REGION, quarter="2020Q1", index_value=100.0))
    session.add(HousePriceIndex(region=REGION, quarter="2024Q1", index_value=138.0))
    session.add(_estate(region=REGION))
    session.add(_purchase(10000000.0))
    session.commit()

    out = svc.suggest_estate_values(session, "202403")  # → current quarter 2024Q1
    assert len(out) == 1
    s = out[0]
    assert s.cost == 10000000.0
    assert s.suggested_market_value == 13800000.0  # 10M × 138/100
    assert s.obtain_quarter == "2020Q1"
    assert s.current_quarter == "2024Q1"
    assert s.region == REGION


def test_suggest_falls_back_to_national(session: Session) -> None:
    # Estate is in a region with no index data → falls back to 全國.
    session.add(HousePriceIndex(region=svc.DEFAULT_REGION, quarter="2020Q1", index_value=100.0))
    session.add(HousePriceIndex(region=svc.DEFAULT_REGION, quarter="2024Q1", index_value=150.0))
    session.add(_estate(region="新北市"))  # 新北市 has no rows
    session.add(_purchase(8000000.0))
    session.commit()

    s = svc.suggest_estate_values(session, "202403")[0]
    assert s.region == svc.DEFAULT_REGION
    assert s.suggested_market_value == 12000000.0  # 8M × 150/100 via 全國


def test_suggest_null_when_index_missing(session: Session) -> None:
    session.add(_estate())
    session.add(_purchase(10000000.0))
    session.commit()

    out = svc.suggest_estate_values(session, "202403")
    assert out[0].suggested_market_value is None  # no index rows at all


def test_refresh_index_endpoint(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(svc, "_fetch_index_rows", lambda d, c: [("2024Q1", 137.73)])
    r = client.post("/monthly-report/estate-values/refresh-index")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["ok"] is True
    assert data["upserted"] == 1
    assert data["region"] == REGION


def test_suggestions_endpoint(client: TestClient, session: Session) -> None:
    session.add(HousePriceIndex(region=REGION, quarter="2020Q1", index_value=100.0))
    session.add(HousePriceIndex(region=REGION, quarter="2024Q1", index_value=150.0))
    session.add(_estate(region=REGION))
    session.add(_purchase(8000000.0))
    session.commit()

    r = client.get("/monthly-report/estate-values/202403/suggestions")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data[0]["suggested_market_value"] == 12000000.0  # 8M × 150/100
