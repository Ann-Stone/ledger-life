"""Expenditure trend endpoint (BE-025)."""
from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.models.reports.expenditure import ExpenditureTrendRead
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    error_response,
    not_found_error,
)
from app.services.report_service import get_expenditure_trend

router = APIRouter()


@router.get(
    "/expenditure/{type}",
    summary="Get expenditure trend",
    description=(
        "Returns monthly (12 points) or yearly (10 points) expenditure aggregated "
        "from Journal rows whose action_main_type is Floating or Fixed."
    ),
    response_model=ApiResponse[ExpenditureTrendRead],
    responses={
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def get_expenditure(
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
) -> ApiResponse[ExpenditureTrendRead]:
    return ApiResponse(data=get_expenditure_trend(session, type, vesting_month))
