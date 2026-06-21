"""Tests for CORS, global exception handlers, and the success envelope."""
from __future__ import annotations

from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.main import app


class _Payload(BaseModel):
    x: int


@app.get("/__raise__/exception", include_in_schema=False)
def _raise_exception() -> None:
    raise RuntimeError("boom")


@app.get("/__raise__/http", include_in_schema=False)
def _raise_http() -> None:
    raise HTTPException(status_code=418, detail="I'm a teapot")


@app.get("/__raise__/value", include_in_schema=False)
def _raise_value() -> None:
    raise ValueError("bad value")


@app.post("/__raise__/validate", include_in_schema=False)
def _validate(payload: _Payload):  # noqa: ANN201 — pydantic handles response
    return {"x": payload.x}


client = TestClient(app, raise_server_exceptions=False)


def test_unhandled_exception_returns_envelope() -> None:
    r = client.get("/__raise__/exception")
    assert r.status_code == 500
    body = r.json()
    assert body["status"] == 0
    assert body["msg"] == "fail"
    assert "boom" in body["error"]


def test_http_exception_preserves_status() -> None:
    r = client.get("/__raise__/http")
    assert r.status_code == 418
    body = r.json()
    assert body["status"] == 0
    assert body["error"] == "I'm a teapot"


def test_value_error_returns_400() -> None:
    r = client.get("/__raise__/value")
    assert r.status_code == 400
    body = r.json()
    assert body["status"] == 0
    assert body["error"] == "bad value"


def test_validation_error_returns_envelope() -> None:
    r = client.post("/__raise__/validate", json={"x": "not-an-int"})
    assert r.status_code == 422
    body = r.json()
    assert body["status"] == 0
    assert isinstance(body["error"], list)
    assert body["error"][0]["type"] == "int_parsing"


def test_success_returns_envelope() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == 1
    assert body["msg"] == "success"
    assert body["data"]["alive"] is True


def test_cors_allows_any_origin() -> None:
    r = client.options(
        "/health",
        headers={
            "Origin": "http://example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert r.headers.get("access-control-allow-origin") == "*"
