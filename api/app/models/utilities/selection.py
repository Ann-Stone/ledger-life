"""Selection group schemas used by /utilities/selections/* endpoints."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SelectionOption(BaseModel):
    value: str = Field(
        ...,
        description="Option value submitted on select",
        examples=["1"],
    )
    label: str = Field(
        ...,
        description="Human-readable label",
        examples=["Cash — NTD"],
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"value": "1", "label": "Cash — NTD"}}
    )


class SelectionGroup(BaseModel):
    label: str = Field(
        ...,
        description="Group label (e.g. account type)",
        examples=["BANK"],
    )
    options: list[SelectionOption] = Field(
        ...,
        description="Options that belong to this group",
        examples=[[{"value": "1", "label": "Cash — NTD"}]],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "label": "BANK",
                "options": [{"value": "1", "label": "Cash — NTD"}],
            }
        }
    )
