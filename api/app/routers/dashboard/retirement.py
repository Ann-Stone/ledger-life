"""Retirement-readiness endpoints (consumption-basis FIRE target + debt health)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.models.dashboard.retirement import (
    RetirementReadinessRead,
    RetirementSettingRead,
    RetirementSettingUpdate,
)
from app.schemas.response import INTERNAL_ERROR, VALIDATION_ERROR, ApiResponse
from app.services.retirement_service import (
    get_retirement_readiness,
    get_retirement_settings,
    update_retirement_settings,
)

router = APIRouter()


@router.get(
    "/retirement",
    summary="Retirement readiness",
    description=(
        "Point-in-time readiness on the consumption basis: target_portfolio = "
        "annual_expense_base / withdrawal_rate (loan excluded from the base), "
        "readiness = net_worth / target. Also returns debt-service-to-income and "
        "per-loan payoff projection for the during-loan cash-flow check."
    ),
    response_model=ApiResponse[RetirementReadinessRead],
    responses={422: VALIDATION_ERROR, 500: INTERNAL_ERROR},
)
def get_dashboard_retirement(
    session: Session = Depends(get_session),
) -> ApiResponse[RetirementReadinessRead]:
    return ApiResponse(data=get_retirement_readiness(session))


@router.get(
    "/retirement-settings",
    summary="Get retirement settings",
    description="Returns the withdrawal rate (default 4%) and optional expense-base override.",
    response_model=ApiResponse[RetirementSettingRead],
    responses={500: INTERNAL_ERROR},
)
def read_retirement_settings(
    session: Session = Depends(get_session),
) -> ApiResponse[RetirementSettingRead]:
    row = get_retirement_settings(session)
    return ApiResponse(data=RetirementSettingRead.model_validate(row, from_attributes=True))


@router.put(
    "/retirement-settings",
    summary="Update retirement settings",
    description=(
        "Upsert the single config row. withdrawal_rate (0.001–0.5) is optional; "
        "annual_expense_override is set verbatim (null clears it)."
    ),
    response_model=ApiResponse[RetirementSettingRead],
    responses={422: VALIDATION_ERROR, 500: INTERNAL_ERROR},
)
def write_retirement_settings(
    payload: RetirementSettingUpdate,
    session: Session = Depends(get_session),
) -> ApiResponse[RetirementSettingRead]:
    row = update_retirement_settings(session, payload)
    return ApiResponse(data=RetirementSettingRead.model_validate(row, from_attributes=True))
