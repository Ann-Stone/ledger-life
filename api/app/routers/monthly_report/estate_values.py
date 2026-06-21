"""Real-estate market-value (估值) management endpoints (Monthly Report domain).

Lets the user record each property's periodic appraisal per month; the
settlement step then values the property at the recorded amount instead of cost.
Mirrors the insurance surrender-value endpoints.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlmodel import Session

from app.database import get_session
from app.models.assets.estate_value_history import (
    EstateValueCreate,
    EstateValueMonthRead,
    EstateValueRead,
)
from app.models.dashboard.house_price_index import (
    EstateValueSuggestion,
    IndexRefreshResult,
)
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    not_found_error,
)
from app.services.estate_value_service import (
    list_month_estate_values,
    upsert_estate_value,
)
from app.services.house_price_index_service import (
    refresh_index,
    suggest_estate_values,
)

router = APIRouter()


_VESTING_MONTH = Annotated[
    str,
    Path(..., pattern=r"^\d{6}$", description="YYYYMM", examples=["202604"]),
]


@router.get(
    "/{vesting_month}",
    summary="Month-level market values for every property",
    description=(
        "For every real-estate holding, return the latest recorded market value "
        "(估值) on or before month-end (carried forward), with a ``recorded`` flag "
        "that is true only when entered in this exact month."
    ),
    response_model=ApiResponse[list[EstateValueMonthRead]],
    responses={422: VALIDATION_ERROR, 500: INTERNAL_ERROR},
)
def get_estate_values_by_month(
    vesting_month: _VESTING_MONTH,
    session: Session = Depends(get_session),
) -> ApiResponse[list[EstateValueMonthRead]]:
    return ApiResponse(data=list_month_estate_values(session, vesting_month))


@router.post(
    "",
    summary="Record (insert or update) a property's market value for a month",
    description=(
        "Upsert the 估值 for an (estate, month). Idempotent on the composite key; "
        "404 when the estate does not exist."
    ),
    response_model=ApiResponse[EstateValueRead],
    status_code=201,
    responses={
        404: not_found_error("Estate"),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def post_estate_value(
    payload: EstateValueCreate, session: Session = Depends(get_session)
) -> ApiResponse[EstateValueRead]:
    row = upsert_estate_value(session, payload)
    return ApiResponse(data=EstateValueRead.model_validate(row, from_attributes=True))


@router.post(
    "/refresh-index",
    summary="Refresh the house-price index from data.gov.tw (best-effort)",
    description=(
        "Pull the latest 住宅價格指數 (repeat-sales, market-based) from data.gov.tw "
        "open data and upsert the quarterly series. Best-effort: on a fetch/parse "
        "failure it keeps the existing data and returns ok=false."
    ),
    response_model=ApiResponse[IndexRefreshResult],
    responses={500: INTERNAL_ERROR},
)
def post_refresh_index(
    session: Session = Depends(get_session),
) -> ApiResponse[IndexRefreshResult]:
    return ApiResponse(data=refresh_index(session))


@router.get(
    "/{vesting_month}/suggestions",
    summary="Index-based suggested market value per property",
    description=(
        "For each estate, suggest a market value = acquisition cost × (current "
        "index / obtain-quarter index), using the configured house-price index "
        "region. suggested_market_value is null when the index is unavailable. "
        "The suggestion is advisory — a recorded value always overrides it."
    ),
    response_model=ApiResponse[list[EstateValueSuggestion]],
    responses={422: VALIDATION_ERROR, 500: INTERNAL_ERROR},
)
def get_estate_value_suggestions(
    vesting_month: _VESTING_MONTH,
    session: Session = Depends(get_session),
) -> ApiResponse[list[EstateValueSuggestion]]:
    return ApiResponse(data=suggest_estate_values(session, vesting_month))


__all__ = ["router"]
