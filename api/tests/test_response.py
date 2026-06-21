"""Tests for the unified response envelopes."""
from __future__ import annotations

from app.schemas.response import ApiError, ApiResponse


def test_api_response_shape() -> None:
    """ApiResponse carries status=1 / msg="success" by default and a typed payload."""
    payload = {"pong": True}
    resp = ApiResponse[dict](data=payload)

    dumped = resp.model_dump()
    assert dumped["status"] == 1
    assert dumped["msg"] == "success"
    assert dumped["data"] == payload


def test_api_error_shape() -> None:
    """ApiError carries status=0 / msg="fail" by default and a serialisable error."""
    err = ApiError(error="ValueError: bad input")

    dumped = err.model_dump()
    assert dumped["status"] == 0
    assert dumped["msg"] == "fail"
    assert dumped["error"] == "ValueError: bad input"
