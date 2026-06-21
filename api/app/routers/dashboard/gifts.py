"""Dashboard gifts endpoint (BE-028)."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlmodel import Session

from app.database import get_session
from app.models.dashboard.gift_view import GiftItem
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    error_response,
    not_found_error,
)
from app.services.dashboard_service import get_gifted_by_year

router = APIRouter()


@router.get(
    "/gifts/{year}",
    summary="Gifted amounts by year",
    description=(
        "Returns cross-owner Transfer totals grouped by sender (Account.owner). "
        "Rate is amount * 100 / 2,200,000 (legacy gift-tax threshold)."
    ),
    response_model=ApiResponse[list[GiftItem]],
    responses={
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def get_dashboard_gifts(
    year: Annotated[
        str,
        Path(..., description="YYYY", examples=["2026"], pattern=r"^\d{4}$"),
    ],
    session: Session = Depends(get_session),
) -> ApiResponse[list[GiftItem]]:
    return ApiResponse(data=get_gifted_by_year(session, year))
