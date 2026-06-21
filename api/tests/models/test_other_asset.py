"""Field-level tests for OtherAsset table."""
from __future__ import annotations

from app.models.assets.other_asset import (
    OtherAsset,
    OtherAssetCreate,
    OtherAssetRead,
    OtherAssetUpdate,
)


def test_other_asset_fields() -> None:
    table = OtherAsset.__table__
    assert OtherAsset.__tablename__ == "Other_Asset"
    assert table.c.asset_id.primary_key is True

    expected = {"asset_id", "asset_name", "asset_type", "in_use", "asset_index"}
    assert set(table.c.keys()) == expected

    for cls in (OtherAsset, OtherAssetCreate, OtherAssetUpdate, OtherAssetRead):
        js = cls.model_json_schema()
        assert "example" in js
        for n, p in js["properties"].items():
            assert "description" in p, n
            assert "examples" in p, n
