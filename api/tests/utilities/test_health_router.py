"""Router tests for /health."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.routers import health as health_module


def test_version_resolution(monkeypatch) -> None:
    # Real resolution: either a known version, or fallback "0.0.0".
    assert isinstance(health_module._resolve_version(), str)
    assert health_module._resolve_version()  # non-empty

    # Force fallback path.
    def _raise(_name: str) -> str:
        raise health_module.PackageNotFoundError(_name)

    monkeypatch.setattr(health_module, "version", _raise)
    assert health_module._resolve_version() == "0.0.0"


def test_health_returns_alive_and_version(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == 1
    assert body["data"]["alive"] is True
    assert isinstance(body["data"]["version"], str)
    assert body["data"]["version"] != ""


def test_health_works_without_db(client: TestClient, monkeypatch) -> None:
    """Health must succeed even if the DB session dependency would error."""
    from app.database import get_session

    def _broken():
        raise RuntimeError("db unavailable")
        yield  # pragma: no cover

    # Override only for this test scope; the client fixture already cleans up.
    client.app.dependency_overrides[get_session] = _broken
    try:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["data"]["alive"] is True
    finally:
        client.app.dependency_overrides.pop(get_session, None)
