"""Dashboard target settings endpoints (BE-027)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.models.dashboard.target_setting import (
    TargetSettingCreate,
    TargetSettingRead,
    TargetSettingUpdate,
)
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    error_response,
    not_found_error,
)
from app.services.dashboard_service import (
    create_target,
    delete_target,
    list_targets,
    update_target,
)

router = APIRouter()


@router.get(
    "/targets",
    summary="List annual targets",
    description="Returns all target settings ordered by year desc.",
    response_model=ApiResponse[list[TargetSettingRead]],
    responses={422: VALIDATION_ERROR, 500: INTERNAL_ERROR},
)
def list_dashboard_targets(
    session: Session = Depends(get_session),
) -> ApiResponse[list[TargetSettingRead]]:
    rows = list_targets(session)
    return ApiResponse(
        data=[TargetSettingRead.model_validate(r, from_attributes=True) for r in rows]
    )


@router.post(
    "/targets",
    summary="Create target",
    description=(
        "Creates a target. target_year defaults to current year; is_done defaults to N."
    ),
    response_model=ApiResponse[TargetSettingRead],
    responses={
        409: error_response("Duplicate distinct_number", error_payload="Duplicate distinct_number"),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def create_dashboard_target(
    payload: TargetSettingCreate,
    session: Session = Depends(get_session),
) -> ApiResponse[TargetSettingRead]:
    row = create_target(session, payload)
    return ApiResponse(data=TargetSettingRead.model_validate(row, from_attributes=True))


@router.put(
    "/targets/{target_id}",
    summary="Update target",
    description="Partial update. is_done can be changed independently.",
    response_model=ApiResponse[TargetSettingRead],
    responses={
        404: not_found_error("Target"),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def update_dashboard_target(
    target_id: str,
    payload: TargetSettingUpdate,
    session: Session = Depends(get_session),
) -> ApiResponse[TargetSettingRead]:
    row = update_target(session, target_id, payload)
    return ApiResponse(data=TargetSettingRead.model_validate(row, from_attributes=True))


@router.delete(
    "/targets/{target_id}",
    summary="Delete target",
    description="Deletes a target by id.",
    response_model=ApiResponse[dict],
    responses={
        422: VALIDATION_ERROR,
        404: not_found_error("Target"),
        500: INTERNAL_ERROR,
    },
)
def delete_dashboard_target(
    target_id: str,
    session: Session = Depends(get_session),
) -> ApiResponse[dict]:
    delete_target(session, target_id)
    return ApiResponse(data={"deleted": target_id})
