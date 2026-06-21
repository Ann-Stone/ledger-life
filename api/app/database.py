"""Database engine, session factory, and schema helpers."""
from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

SQLITE_PREFIX = "sqlite:///"


def _resolve_sqlite_url(url: str) -> str:
    """Expand `~` and ensure the parent directory exists for SQLite URLs.

    Non-SQLite URLs are returned unchanged. For `sqlite:///~/...` and
    `sqlite:///./...` relative forms, the path is made absolute so that both
    the engine and Alembic observe the same file regardless of CWD.
    """
    if not url.startswith(SQLITE_PREFIX):
        return url

    raw_path = url[len(SQLITE_PREFIX):]
    # Allow `sqlite:///:memory:` to pass through.
    if raw_path == ":memory:":
        return url

    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    return f"{SQLITE_PREFIX}{path}"


engine = create_engine(
    _resolve_sqlite_url(settings.database_url),
    echo=settings.debug,
    connect_args={"check_same_thread": False},
)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a request-scoped SQLModel session."""
    with Session(engine) as session:
        yield session


def create_db_and_tables() -> None:
    """Create all tables registered on SQLModel.metadata."""
    SQLModel.metadata.create_all(engine)
