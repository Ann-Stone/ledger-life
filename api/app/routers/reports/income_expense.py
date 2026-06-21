"""Income statement (收支表) endpoint — per-period income/expense + savings rate."""
from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.models.reports.income_expense import IncomeExpenseReportRead
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
)
from app.services.report_service import get_income_expense_report

router = APIRouter()


@router.get(
    "/income-expense/{type}",
    summary="Get income vs expense + savings rate",
    description=(
        "Returns monthly (12 points) or yearly (10 points) income / fixed / "
        "floating / net per period, plus an annual summary (total income, total "
        "expense, net savings, savings rate). Amounts are FX-converted to the base "
        "currency; invest and transfer rows are excluded."
    ),
    response_model=ApiResponse[IncomeExpenseReportRead],
    responses={
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def get_income_expense(
    type: Literal["monthly", "yearly"],
    vesting_month: Annotated[
        str,
        Query(
            ...,
            description="Anchor month YYYYMM",
            examples=["202412"],
            pattern=r"^\d{6}$",
        ),
    ],
    session: Session = Depends(get_session),
) -> ApiResponse[IncomeExpenseReportRead]:
    return ApiResponse(data=get_income_expense_report(session, type, vesting_month))
