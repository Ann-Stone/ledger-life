"""Insurance surrender-value (解約金) management endpoints (Monthly Report domain).

Lets the user record each savings policy's contractual surrender value per month;
the settlement step then values the policy at the recorded amount instead of the
net-premium estimate. Mirrors the stock-price endpoints.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlmodel import Session

from app.database import get_session
from app.models.assets.insurance_value_history import (
    InsuranceValueCreate,
    InsuranceValueMonthRead,
    InsuranceValueRead,
)
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    not_found_error,
)
from app.services.insurance_value_service import (
    list_month_insurance_values,
    upsert_insurance_value,
)

router = APIRouter()


_VESTING_MONTH = Annotated[
    str,
    Path(..., pattern=r"^\d{6}$", description="YYYYMM", examples=["202604"]),
]


@router.get(
    "/{vesting_month}",
    summary="Month-level surrender values for every policy",
    description=(
        "For every insurance policy, return the latest recorded surrender value "
        "(解約金) on or before month-end (carried forward), with a ``recorded`` "
        "flag that is true only when entered in this exact month."
    ),
    response_model=ApiResponse[list[InsuranceValueMonthRead]],
    responses={422: VALIDATION_ERROR, 500: INTERNAL_ERROR},
)
def get_insurance_values_by_month(
    vesting_month: _VESTING_MONTH,
    session: Session = Depends(get_session),
) -> ApiResponse[list[InsuranceValueMonthRead]]:
    return ApiResponse(data=list_month_insurance_values(session, vesting_month))


@router.post(
    "",
    summary="Record (insert or update) a policy's surrender value for a month",
    description=(
        "Upsert the 解約金 for a (policy, month). Idempotent on the composite key; "
        "404 when the policy does not exist."
    ),
    response_model=ApiResponse[InsuranceValueRead],
    status_code=201,
    responses={
        404: not_found_error("Insurance"),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def post_insurance_value(
    payload: InsuranceValueCreate, session: Session = Depends(get_session)
) -> ApiResponse[InsuranceValueRead]:
    row = upsert_insurance_value(session, payload)
    return ApiResponse(data=InsuranceValueRead.model_validate(row, from_attributes=True))


__all__ = ["router"]
