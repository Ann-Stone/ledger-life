"""BE-028 — gift schema tests."""
from __future__ import annotations

from app.models.dashboard.gift_view import GiftItem


def test_gift_item_example() -> None:
    js = GiftItem.model_json_schema()
    assert "example" in js
    for n, p in js["properties"].items():
        assert "description" in p
