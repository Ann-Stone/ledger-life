"""Monthly balance settlement endpoint (BE-019)."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlmodel import Session

from app.database import get_session
from app.models.monthly_report.settlement import SettlementResult
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    error_response,
    not_found_error,
)
from app.services.settlement_service import settle

router = APIRouter()


_VESTING_MONTH = Annotated[
    str,
    Path(
        ...,
        pattern=r"^\d{6}$",
        description="YYYYMM",
        examples=["202604"],
    ),
]


@router.put(
    "/{vesting_month}/settle",
    summary="Run monthly balance settlement",
    description=(
        "Snapshot every asset/liability net value for the vesting month. "
        "Idempotent: per-asset-type tables are delete+reinsert; AccountBalance "
        "and CreditCardBalance use cascade-delete from the target month forward "
        "to invalidate later carry-forward snapshots."
    ),
    response_model=ApiResponse[SettlementResult],
    responses={
        422: VALIDATION_ERROR,
        404: error_response("Vesting month has no eligible data", error_payload="Vesting month has no eligible data"),
        500: INTERNAL_ERROR,
    },
)
def put_settle(
    vesting_month: _VESTING_MONTH,
    session: Session = Depends(get_session),
) -> ApiResponse[SettlementResult]:
    try:
        result = settle(session, vesting_month)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Settlement failed: {exc}")
    return ApiResponse(data=result)


__all__ = ["router"]
