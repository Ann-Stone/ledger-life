"""Budget variance (預算 vs 實際) endpoint — annual expected vs actual per category."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlmodel import Session

from app.database import get_session
from app.models.reports.budget_variance import BudgetVarianceRead
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
)
from app.services.report_service import get_budget_variance

router = APIRouter()


@router.get(
    "/budget-variance/{year}",
    summary="Get annual budget vs actual variance",
    description=(
        "Per expense category: annual expected (Budget sum of expected01..12, or "
        "annual_amount for annual-event categories) vs actual FX-converted spend "
        "for the year, with diff, usage rate, and a run-rate projection. Income, "
        "invest and transfer categories are excluded."
    ),
    response_model=ApiResponse[BudgetVarianceRead],
    responses={
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def get_budget(
    year: Annotated[
        str,
        Path(description="Budget year YYYY", examples=["2026"], pattern=r"^\d{4}$"),
    ],
    session: Session = Depends(get_session),
) -> ApiResponse[BudgetVarianceRead]:
    return ApiResponse(data=get_budget_variance(session, year))
