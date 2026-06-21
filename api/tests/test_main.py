"""Tests for app.main lifespan and router registration."""
from __future__ import annotations

import importlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


def test_lifespan_creates_tables(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The FastAPI lifespan hook materialises the SQLite DB on startup."""
    target = tmp_path / "lifespan.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{target}")

    import app.config as cfg
    import app.database as db
    import app.main as main

    importlib.reload(cfg)
    importlib.reload(db)
    importlib.reload(main)

    with TestClient(main.app):
        pass

    assert target.exists()
