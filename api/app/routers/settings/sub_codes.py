"""Sub-code CRUD endpoints (Settings domain)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.models.settings.code_data import CodeDataCreate, CodeDataRead, CodeDataUpdate
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    error_response,
    not_found_error,
)
from app.services.setting_service import (
    create_sub_code,
    delete_sub_code,
    update_sub_code,
)

router = APIRouter(prefix="/sub-codes", tags=["settings:sub-codes"])


@router.post(
    "",
    summary="Create sub-code",
    description=(
        "Create a sub-code. parent_id must reference an existing main code "
        "(404 otherwise)."
    ),
    response_model=ApiResponse[CodeDataRead],
    responses={
        404: not_found_error("Parent code"),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def create_sub_code_endpoint(
    payload: CodeDataCreate,
    session: Session = Depends(get_session),
) -> ApiResponse[CodeDataRead]:
    code = create_sub_code(session, payload)
    return ApiResponse(data=CodeDataRead.model_validate(code, from_attributes=True))


@router.put(
    "/{code_id}",
    summary="Update sub-code",
    description="Update a sub-code by code_id. Returns 404 if not found.",
    response_model=ApiResponse[CodeDataRead],
    responses={
        404: not_found_error("Sub-code"),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def update_sub_code_endpoint(
    code_id: str,
    payload: CodeDataUpdate,
    session: Session = Depends(get_session),
) -> ApiResponse[CodeDataRead]:
    code = update_sub_code(session, code_id, payload)
    return ApiResponse(data=CodeDataRead.model_validate(code, from_attributes=True))


@router.delete(
    "/{code_id}",
    summary="Delete sub-code",
    description="Delete a sub-code by code_id. Returns 404 if not found. No cascading.",
    response_model=ApiResponse[dict],
    responses={
        422: VALIDATION_ERROR,
        404: not_found_error("Sub-code"),
        500: INTERNAL_ERROR,
    },
)
def delete_sub_code_endpoint(
    code_id: str,
    session: Session = Depends(get_session),
) -> ApiResponse[dict]:
    delete_sub_code(session, code_id)
    return ApiResponse(data={"code_id": code_id})
