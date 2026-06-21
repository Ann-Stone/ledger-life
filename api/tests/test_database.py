"""Tests for app.database."""
from __future__ import annotations

import importlib
from pathlib import Path

import pytest
from sqlmodel import Session


def test_resolve_sqlite_url_expands_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`~` expands to the user's home and parent dirs are created."""
    from app.database import _resolve_sqlite_url

    monkeypatch.setenv("HOME", str(tmp_path))
    resolved = _resolve_sqlite_url("sqlite:///~/nested/dir/test.db")

    assert resolved.startswith("sqlite:///")
    db_path = Path(resolved[len("sqlite:///"):])
    assert db_path.is_absolute()
    assert str(tmp_path) in str(db_path)
    assert db_path.parent.exists()


def test_engine_uses_configured_url(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Engine URL reflects the configured DATABASE_URL after reload."""
    target = tmp_path / "engine-url.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{target}")

    import app.config as cfg
    import app.database as db

    importlib.reload(cfg)
    importlib.reload(db)

    assert str(target) in str(db.engine.url)


def test_get_session_yields_session() -> None:
    """`get_session` is a generator that yields a SQLModel Session."""
    from app.database import get_session

    gen = get_session()
    session = next(gen)
    try:
        assert isinstance(session, Session)
    finally:
        gen.close()


def test_create_db_and_tables_creates_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Calling create_db_and_tables materialises the SQLite file."""
    target = tmp_path / "created.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{target}")

    import app.config as cfg
    import app.database as db

    importlib.reload(cfg)
    importlib.reload(db)

    db.create_db_and_tables()

    assert target.exists()


def test_custom_database_url_is_honored(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A custom DATABASE_URL override routes writes to that path."""
    target = tmp_path / "custom.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{target}")

    import app.config as cfg
    import app.database as db

    importlib.reload(cfg)
    importlib.reload(db)

    db.create_db_and_tables()

    assert target.exists()
