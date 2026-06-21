"""Dashboard upcoming alarms endpoint (BE-028)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.models.dashboard.alarm_view import AlarmItem
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    error_response,
    not_found_error,
)
from app.services.dashboard_service import get_upcoming_alarms

router = APIRouter()


@router.get(
    "/alarms",
    summary="List upcoming alarms",
    description=(
        "Returns alarms scheduled within today..today+6 months. Monthly-recurring "
        "alarms are expanded per month; expired months are excluded."
    ),
    response_model=ApiResponse[list[AlarmItem]],
    responses={422: VALIDATION_ERROR, 500: INTERNAL_ERROR},
)
def list_dashboard_alarms(
    session: Session = Depends(get_session),
) -> ApiResponse[list[AlarmItem]]:
    return ApiResponse(data=get_upcoming_alarms(session))
