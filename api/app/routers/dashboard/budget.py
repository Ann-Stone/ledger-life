"""Dashboard budget endpoint (BE-026)."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.models.dashboard.budget import BudgetRead, BudgetType
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    error_response,
    not_found_error,
)
from app.services.dashboard_service import get_budget_usage

router = APIRouter()


@router.get(
    "/budget",
    summary="Get budget vs actual",
    description=(
        "Returns per-category budget-vs-actual for a month (YYYYMM) or year (YYYY)."
    ),
    response_model=ApiResponse[BudgetRead],
    responses={
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def get_dashboard_budget(
    type: Annotated[
        BudgetType,
        Query(..., description="Aggregation granularity", examples=["monthly"]),
    ],
    period: Annotated[
        str,
        Query(
            ...,
            description="YYYYMM for monthly, YYYY for yearly",
            examples=["202403"],
            pattern=r"^\d{4}(\d{2})?$",
        ),
    ],
    session: Session = Depends(get_session),
) -> ApiResponse[BudgetRead]:
    return ApiResponse(data=get_budget_usage(session, type, period))
