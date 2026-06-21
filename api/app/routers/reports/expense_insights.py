"""Expense insights (年度洞察) endpoint — YoY by category + largest transactions."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlmodel import Session

from app.database import get_session
from app.models.reports.expense_insights import ExpenseInsightsRead
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
)
from app.services.report_service import get_expense_insights

router = APIRouter()


@router.get(
    "/expense-insights/{year}",
    summary="Get year-over-year change + largest transactions",
    description=(
        "Per expense category: this year vs prior-year actual with YoY rate "
        "(ordered by absolute change), plus the year's largest individual expense "
        "transactions. FX-converted; only Fixed/Floating rows count."
    ),
    response_model=ApiResponse[ExpenseInsightsRead],
    responses={
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def get_insights(
    year: Annotated[
        str,
        Path(description="Calendar year YYYY", examples=["2026"], pattern=r"^\d{4}$"),
    ],
    session: Session = Depends(get_session),
) -> ApiResponse[ExpenseInsightsRead]:
    return ApiResponse(data=get_expense_insights(session, year))
