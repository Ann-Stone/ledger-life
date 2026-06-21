"""Unified response envelopes used by every endpoint."""
from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Successful response envelope."""

    status: int = Field(
        1,
        description="1 = success, 0 = fail",
        examples=[1],
    )
    data: T | None = Field(
        None,
        description="Response payload. Shape depends on the endpoint.",
    )
    msg: str = Field(
        "success",
        description="Human-readable status message",
        examples=["success"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"status": 1, "data": None, "msg": "success"},
        }
    )


class ApiError(BaseModel):
    """Failure response envelope."""

    status: int = Field(
        0,
        description="Always 0 for failure",
        examples=[0],
    )
    error: dict | list | str | None = Field(
        None,
        description="Error payload. A string for simple errors, or a list/dict for validation details.",
        examples=["ValueError: bad input"],
    )
    msg: str = Field(
        "fail",
        description="Human-readable status message",
        examples=["fail"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": 0,
                "error": "ValueError: bad input",
                "msg": "fail",
            },
        }
    )


def error_response(
    description: str,
    error_payload: str | dict | list = "ValueError: bad input",
) -> dict[str, Any]:
    """Build an OpenAPI response definition for an error code.

    Returned dict is the value side of the FastAPI ``responses={status: ...}``
    parameter. Includes:

    - ``model``: ``ApiError`` so the schema is referenced in the spec.
    - ``description``: shown in Swagger UI and consumed by the api-reference
      generator.
    - ``content.application/json.example``: a concrete ``ApiError`` instance
      so frontend agents can plan UX (toasts, form errors, retries) without
      reading router source.

    The ``error_payload`` should be a realistic value the endpoint actually
    emits — e.g. ``"Account 42 not found"`` for a 404, or a list of pydantic
    validation errors for a 422.
    """
    return {
        "model": ApiError,
        "description": description,
        "content": {
            "application/json": {
                "example": {
                    "status": 0,
                    "error": error_payload,
                    "msg": "fail",
                }
            }
        },
    }


# --- Common error templates ---------------------------------------------------
# Pre-built shorthands for the most repetitive cases. Use these when no
# endpoint-specific error message is needed; otherwise call ``error_response``
# directly with a customised payload.

VALIDATION_ERROR: dict[str, Any] = error_response(
    "Validation error — request payload failed Pydantic validation",
    error_payload=[
        {
            "type": "missing",
            "loc": ["body", "field_name"],
            "msg": "Field required",
            "input": {},
        }
    ],
)

INTERNAL_ERROR: dict[str, Any] = error_response(
    "Unhandled server error — wrapped by global exception handler",
    error_payload="RuntimeError: unexpected failure",
)


def not_found_error(resource: str, sample_id: str | int = 42) -> dict[str, Any]:
    """Shorthand for 404 responses. ``resource`` is shown in the description and example."""
    return error_response(
        f"{resource} not found",
        error_payload=f"{resource} {sample_id} not found",
    )
