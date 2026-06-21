"""Shared pytest fixtures for the networth-api tests."""
from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401  registers every table on SQLModel.metadata
from app.config import settings
from app.database import get_session
from app.main import app


@pytest.fixture(autouse=True)
def _disable_startup_catch_up(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the app lifespan from firing real FX/stock network calls in tests.

    The ``client`` fixture enters ``TestClient(app)`` as a context manager, which
    runs the lifespan; without this the startup catch-up would hit Sinopac and
    yfinance for real on every client-using test.
    """
    monkeypatch.setattr(settings, "enable_startup_catch_up", False)


@pytest.fixture
def session() -> Generator[Session, None, None]:
    """Yield a throw-away SQLModel session backed by in-memory SQLite."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


@pytest.fixture
def client(session: Session) -> Generator[TestClient, None, None]:
    """Yield a TestClient whose get_session dependency returns ``session``."""

    def _override() -> Generator[Session, None, None]:
        yield session

    app.dependency_overrides[get_session] = _override
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(get_session, None)
