"""Dashboard summary endpoint (BE-026)."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.models.dashboard.summary import SummaryRead, SummaryType
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    error_response,
    not_found_error,
)
from app.services.dashboard_service import get_summary

router = APIRouter()


@router.get(
    "/summary",
    summary="Get dashboard summary",
    description=(
        "Returns spending / freedom_ratio / asset_debt_trend time series "
        "for the requested period (YYYYMM-YYYYMM)."
    ),
    response_model=ApiResponse[SummaryRead],
    responses={
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def get_dashboard_summary(
    type: Annotated[
        SummaryType,
        Query(..., description="Summary variant", examples=["spending"]),
    ],
    period: Annotated[
        str,
        Query(
            ...,
            description="YYYYMM-YYYYMM",
            examples=["202301-202312"],
            pattern=r"^\d{6}-\d{6}$",
        ),
    ],
    session: Session = Depends(get_session),
) -> ApiResponse[SummaryRead]:
    return ApiResponse(data=get_summary(session, type, period))
