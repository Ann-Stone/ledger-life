"""Main Code CRUD endpoints (Settings domain)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.models.settings.code_data import (
    CodeDataCreate,
    CodeDataRead,
    CodeDataUpdate,
    CodeWithSubs,
)
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    error_response,
    not_found_error,
)
from app.services.setting_service import (
    create_main_code,
    delete_main_code,
    list_codes_with_sub_codes,
    list_main_codes,
    list_sub_codes,
    update_main_code,
)

router = APIRouter(prefix="/codes", tags=["settings:codes"])


@router.get(
    "",
    summary="List main codes",
    description="List all main (top-level) codes ordered by code_index.",
    response_model=ApiResponse[list[CodeDataRead]],
    responses={422: VALIDATION_ERROR, 500: INTERNAL_ERROR},
)
def list_codes_endpoint(session: Session = Depends(get_session)) -> ApiResponse[list[CodeDataRead]]:
    rows = list_main_codes(session)
    return ApiResponse(data=[CodeDataRead.model_validate(r, from_attributes=True) for r in rows])


@router.get(
    "/all-with-sub",
    summary="Full code tree",
    description="Return all main codes with their sub-codes nested under sub_codes.",
    response_model=ApiResponse[list[CodeWithSubs]],
    responses={422: VALIDATION_ERROR, 500: INTERNAL_ERROR},
)
def list_codes_with_sub_endpoint(
    session: Session = Depends(get_session),
) -> ApiResponse[list[CodeWithSubs]]:
    return ApiResponse(data=list_codes_with_sub_codes(session))


@router.post(
    "",
    summary="Create main code",
    description=(
        "Create a main code. If code_type is Fixed or Floating, a Budget row "
        "for the current year is auto-inserted with all monthly amounts set to 0."
    ),
    response_model=ApiResponse[CodeDataRead],
    responses={
        409: error_response("Duplicate code_id", error_payload="Duplicate code_id"),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def create_code_endpoint(
    payload: CodeDataCreate,
    session: Session = Depends(get_session),
) -> ApiResponse[CodeDataRead]:
    code = create_main_code(session, payload)
    return ApiResponse(data=CodeDataRead.model_validate(code, from_attributes=True))


@router.put(
    "/{code_id}",
    summary="Update main code",
    description="Update a main code by code_id. Returns 404 if not found.",
    response_model=ApiResponse[CodeDataRead],
    responses={
        404: not_found_error("Code"),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def update_code_endpoint(
    code_id: str,
    payload: CodeDataUpdate,
    session: Session = Depends(get_session),
) -> ApiResponse[CodeDataRead]:
    code = update_main_code(session, code_id, payload)
    return ApiResponse(data=CodeDataRead.model_validate(code, from_attributes=True))


@router.delete(
    "/{code_id}",
    summary="Delete main code",
    description="Delete a main code by code_id. Returns 404 if not found.",
    response_model=ApiResponse[dict],
    responses={
        422: VALIDATION_ERROR,
        404: not_found_error("Code"),
        500: INTERNAL_ERROR,
    },
)
def delete_code_endpoint(
    code_id: str,
    session: Session = Depends(get_session),
) -> ApiResponse[dict]:
    delete_main_code(session, code_id)
    return ApiResponse(data={"code_id": code_id})


@router.get(
    "/{parent_id}/sub-codes",
    summary="List sub-codes of a parent",
    description="List sub-codes belonging to a main code, ordered by code_index.",
    response_model=ApiResponse[list[CodeDataRead]],
    responses={
        422: VALIDATION_ERROR,
        404: not_found_error("Parent code"),
        500: INTERNAL_ERROR,
    },
)
def list_sub_codes_endpoint(
    parent_id: str,
    session: Session = Depends(get_session),
) -> ApiResponse[list[CodeDataRead]]:
    rows = list_sub_codes(session, parent_id)
    return ApiResponse(data=[CodeDataRead.model_validate(r, from_attributes=True) for r in rows])
