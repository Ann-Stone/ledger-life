"""Balance sheet endpoint (BE-025)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.models.reports.balance import BalanceSheetRead
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    error_response,
    not_found_error,
)
from app.services.report_service import get_balance_sheet

router = APIRouter()


@router.get(
    "/balance",
    summary="Get current balance sheet",
    description=(
        "Aggregates latest snapshots per asset/liability entity, FX-converts to base "
        "currency, returns net worth."
    ),
    response_model=ApiResponse[BalanceSheetRead],
    responses={422: VALIDATION_ERROR, 500: INTERNAL_ERROR},
)
def get_balance(session: Session = Depends(get_session)) -> ApiResponse[BalanceSheetRead]:
    return ApiResponse(data=get_balance_sheet(session))
