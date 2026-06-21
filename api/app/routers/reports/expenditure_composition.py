"""Expenditure composition (支出結構) endpoint — category→subcategory tree."""
from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.models.reports.expenditure_composition import ExpenditureCompositionRead
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
)
from app.services.report_service import get_expenditure_composition

router = APIRouter()


@router.get(
    "/expenditure-composition/{type}",
    summary="Get expenditure composition tree",
    description=(
        "Category → subcategory tree of expense magnitude over the monthly "
        "(trailing 12 months) or yearly (trailing 10 years) window, each node "
        "carrying its share of the grand total. FX-converted to base currency; "
        "only Fixed and Floating rows are counted."
    ),
    response_model=ApiResponse[ExpenditureCompositionRead],
    responses={
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def get_composition(
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
) -> ApiResponse[ExpenditureCompositionRead]:
    return ApiResponse(data=get_expenditure_composition(session, type, vesting_month))
