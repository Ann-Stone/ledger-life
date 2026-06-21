"""Alarm / reminder endpoints (Settings domain)."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.models.settings.alarm import AlarmCreate, AlarmRead, AlarmUpdate
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    error_response,
    not_found_error,
)
from app.services.setting_service import (
    create_alarm,
    delete_alarm,
    list_alarms,
    list_alarms_by_date,
    update_alarm,
)

router = APIRouter(prefix="/alarms", tags=["settings:alarms"])


@router.get(
    "",
    summary="List all alarms",
    description="List every alarm ordered by alarm_id ASC.",
    response_model=ApiResponse[list[AlarmRead]],
    responses={422: VALIDATION_ERROR, 500: INTERNAL_ERROR},
)
def list_alarms_endpoint(
    session: Session = Depends(get_session),
) -> ApiResponse[list[AlarmRead]]:
    rows = list_alarms(session)
    return ApiResponse(
        data=[AlarmRead.model_validate(r, from_attributes=True) for r in rows]
    )


@router.get(
    "/by-date",
    summary="List alarms matching a date",
    description=(
        "Return alarms whose alarm_date equals the query date (e.g. 08/26) "
        "or ends with it (e.g. monthly day 26 matches)."
    ),
    response_model=ApiResponse[list[AlarmRead]],
    responses={
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def list_alarms_by_date_endpoint(
    date: Annotated[
        str,
        Query(description="Date in MM/DD or DD form", examples=["08/26"]),
    ],
    session: Session = Depends(get_session),
) -> ApiResponse[list[AlarmRead]]:
    rows = list_alarms_by_date(session, date)
    return ApiResponse(
        data=[AlarmRead.model_validate(r, from_attributes=True) for r in rows]
    )


@router.post(
    "",
    summary="Create alarm",
    description=(
        "Create an alarm. due_date accepts multiple formats "
        "(ISO 8601, YYYY-MM-DD, YYYYMMDD) and is persisted normalized as YYYYMMDD."
    ),
    response_model=ApiResponse[AlarmRead],
    responses={
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def create_alarm_endpoint(
    payload: AlarmCreate,
    session: Session = Depends(get_session),
) -> ApiResponse[AlarmRead]:
    alarm = create_alarm(session, payload)
    return ApiResponse(data=AlarmRead.model_validate(alarm, from_attributes=True))


@router.put(
    "/{alarm_id}",
    summary="Update alarm",
    description=(
        "Update an alarm by alarm_id. Returns 404 if not found. "
        "due_date is re-normalized when provided."
    ),
    response_model=ApiResponse[AlarmRead],
    responses={
        404: not_found_error("Alarm"),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def update_alarm_endpoint(
    alarm_id: int,
    payload: AlarmUpdate,
    session: Session = Depends(get_session),
) -> ApiResponse[AlarmRead]:
    alarm = update_alarm(session, alarm_id, payload)
    return ApiResponse(data=AlarmRead.model_validate(alarm, from_attributes=True))


@router.delete(
    "/{alarm_id}",
    summary="Delete alarm",
    description="Delete an alarm by alarm_id. Returns 404 if not found.",
    response_model=ApiResponse[dict],
    responses={
        422: VALIDATION_ERROR,
        404: not_found_error("Alarm"),
        500: INTERNAL_ERROR,
    },
)
def delete_alarm_endpoint(
    alarm_id: int,
    session: Session = Depends(get_session),
) -> ApiResponse[dict]:
    delete_alarm(session, alarm_id)
    return ApiResponse(data={"alarm_id": alarm_id})
