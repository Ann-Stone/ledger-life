"""Round-trip smoke test for the Dashboard domain tables."""
from __future__ import annotations

from sqlmodel import Session, select

from app.models.dashboard import FXRate, StockPriceHistory, TargetSetting


def test_dashboard_models_roundtrip(session: Session) -> None:
    fx = FXRate(import_date="20260418", code="USD", buy_rate=31.52)
    sph = StockPriceHistory(
        stock_code="AAPL",
        fetch_date="20260418",
        open_price=180.0,
        highest_price=182.5,
        lowest_price=179.2,
        close_price=181.8,
    )
    tgt = TargetSetting(
        distinct_number="T-2026-01",
        target_year="2026",
        setting_value="Save 1M",
        is_done="N",
    )

    session.add_all([fx, sph, tgt])
    session.commit()

    assert session.exec(select(FXRate)).one().buy_rate == 31.52
    assert session.exec(select(StockPriceHistory)).one().close_price == 181.8
    assert session.exec(select(TargetSetting)).one().setting_value == "Save 1M"
