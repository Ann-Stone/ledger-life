"""Comprehensive income statement (綜合損益表) endpoint — 本業 / 投資 / 綜合."""
from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.models.reports.income_statement import IncomeStatementReportRead
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
)
from app.services.report_service import get_income_statement

router = APIRouter()


@router.get(
    "/income-statement/{type}",
    summary="Get comprehensive income statement (本業/投資/綜合損益)",
    description=(
        "Returns monthly (12 points) or yearly (10 points) profit-and-loss per "
        "period in three sections: 本業損益 (active income − living expenses), "
        "投資損益 (dividends + realized capital gains + unrealized market-value "
        "change), and 綜合損益 (their sum), plus a window summary. Amounts are "
        "FX-converted to the base currency. Realized gains come from booked "
        "資本利得 journals; unrealized covers stock holdings only."
    ),
    response_model=ApiResponse[IncomeStatementReportRead],
    responses={
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def get_income_statement_endpoint(
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
) -> ApiResponse[IncomeStatementReportRead]:
    return ApiResponse(data=get_income_statement(session, type, vesting_month))
