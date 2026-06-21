"""Stock allocation report — service + endpoint tests."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.assets.stock import StockJournal
from app.models.assets.stock_category import StockCategory
from app.models.monthly_report.stock_net_value_history import StockNetValueHistory
from app.models.reports.stock_allocation import (
    StockAllocationRead,
    StockAllocationShare,
)
from app.services.report_service import get_asset_breakdown, get_stock_allocation


def test_schema_examples() -> None:
    for cls in (StockAllocationShare, StockAllocationRead):
        js = cls.model_json_schema()
        assert "example" in js, cls.__name__
        for n, p in js["properties"].items():
            assert "description" in p, f"{cls.__name__}.{n}"
            assert "examples" in p, f"{cls.__name__}.{n}"


def test_empty(session: Session) -> None:
    out = get_stock_allocation(session)
    assert out.total == 0.0
    assert out.items == []


def _seed(session: Session) -> None:
    session.add(StockCategory(category_id="SC-001", name="成長型", in_use="Y", category_index=1))
    session.add(StockCategory(category_id="SC-002", name="債券", in_use="Y", category_index=2))
    holdings = [
        ("STK-1", "SC-001"),       # 成長型
        ("STK-2", "SC-002"),       # 債券
        ("STK-3", None),           # unclassified (null)
        ("STK-4", "SC-DELETED"),   # unclassified (dangling reference)
    ]
    for sid, cid in holdings:
        session.add(
            StockJournal(
                stock_id=sid,
                stock_code=sid,
                stock_name=sid,
                asset_id="AC-1",
                expected_spend=0.0,
                category_id=cid,
            )
        )
    # value = price * fx_rate, mirroring get_asset_breakdown's stock valuation
    snapshots = [("STK-1", 1000.0), ("STK-2", 2000.0), ("STK-3", 500.0), ("STK-4", 500.0)]
    for sid, price in snapshots:
        session.add(
            StockNetValueHistory(
                vesting_month="202604",
                id=sid,
                asset_id="AC-1",
                stock_code=sid,
                stock_name=sid,
                amount=1.0,
                price=price,
                cost=0.0,
                fx_code="TWD",
                fx_rate=1.0,
            )
        )
    session.commit()


def test_golden_split(session: Session) -> None:
    _seed(session)
    out = get_stock_allocation(session)

    assert out.total == 4000.0
    by_name = {i.category_name: i for i in out.items}
    assert by_name["成長型"].amount == 1000.0
    assert by_name["債券"].amount == 2000.0
    # null + dangling both collapse into the unclassified bucket
    assert by_name["未分類"].amount == 1000.0
    assert by_name["未分類"].category_id is None
    # ordered by category_index with unclassified last
    assert [i.category_name for i in out.items] == ["成長型", "債券", "未分類"]
    assert by_name["成長型"].share == 25.0
    assert abs(sum(i.share for i in out.items) - 100.0) < 0.05


def test_reconciles_with_asset_breakdown(session: Session) -> None:
    _seed(session)
    out = get_stock_allocation(session)
    breakdown = get_asset_breakdown(session)
    stocks_bucket = next(i for i in breakdown.items if i.type == "stocks")
    # Per-category total must equal the stocks bucket in the headline breakdown.
    assert out.total == stocks_bucket.amount


def test_latest_month_only(session: Session) -> None:
    session.add(StockCategory(category_id="SC-001", name="成長型", in_use="Y", category_index=1))
    session.add(
        StockJournal(
            stock_id="STK-1", stock_code="A", stock_name="A",
            asset_id="AC-1", expected_spend=0.0, category_id="SC-001",
        )
    )
    session.add(
        StockNetValueHistory(
            vesting_month="202603", id="STK-1", asset_id="AC-1", stock_code="A",
            stock_name="A", amount=1.0, price=100.0, cost=0.0, fx_code="TWD", fx_rate=1.0,
        )
    )
    session.add(
        StockNetValueHistory(
            vesting_month="202604", id="STK-1", asset_id="AC-1", stock_code="A",
            stock_name="A", amount=1.0, price=300.0, cost=0.0, fx_code="TWD", fx_rate=1.0,
        )
    )
    session.commit()

    out = get_stock_allocation(session)
    # Only the latest snapshot (202604, price 300) counts.
    assert out.total == 300.0


def test_endpoint(client: TestClient, session: Session) -> None:
    _seed(session)
    r = client.get("/reports/stock-allocation")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 4000.0
    assert [i["category_name"] for i in data["items"]] == ["成長型", "債券", "未分類"]
