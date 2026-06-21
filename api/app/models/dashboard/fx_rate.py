"""FXRate model — daily FX buy rate snapshot."""
from __future__ import annotations

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


_EXAMPLE = {
    "import_date": "20260418",
    "code": "USD",
    "buy_rate": 31.52,
}


class FXRate(SQLModel, table=True):
    __tablename__ = "FX_Rate"

    import_date: str = Field(..., primary_key=True, description="YYYYMMDD", schema_extra={"examples": ["20260418"]})
    code: str = Field(..., primary_key=True, description="Currency code (USD, JPY, ...)", schema_extra={"examples": ["USD"]})
    buy_rate: float = Field(..., description="Buy rate", schema_extra={"examples": [31.52]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class FXRateCreate(SQLModel):
    import_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20260418"]})
    code: str = Field(..., description="Currency code", schema_extra={"examples": ["USD"]})
    buy_rate: float = Field(..., description="Buy rate", schema_extra={"examples": [31.52]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})


class FXRateUpdate(SQLModel):
    buy_rate: float | None = Field(default=None, description="Buy rate", schema_extra={"examples": [31.55]})

    model_config = ConfigDict(json_schema_extra={"example": {"buy_rate": 31.55}})


class FXRateRead(SQLModel):
    import_date: str = Field(..., description="YYYYMMDD", schema_extra={"examples": ["20260418"]})
    code: str = Field(..., description="Currency code", schema_extra={"examples": ["USD"]})
    buy_rate: float = Field(..., description="Buy rate", schema_extra={"examples": [31.52]})

    model_config = ConfigDict(json_schema_extra={"example": _EXAMPLE})
