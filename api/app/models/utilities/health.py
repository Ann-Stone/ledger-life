"""Health check schema."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class HealthPayload(BaseModel):
    alive: bool = Field(
        ...,
        description="True when the API process is responsive",
        examples=[True],
    )
    version: str = Field(
        ...,
        description="Running app version (from pyproject.toml)",
        examples=["1.0.0"],
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"alive": True, "version": "1.0.0"}}
    )
