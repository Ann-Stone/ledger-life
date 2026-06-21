"""Account CRUD endpoints (Settings domain)."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.models.settings.account import AccountCreate, AccountRead, AccountUpdate
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    error_response,
    not_found_error,
)
from app.services.setting_service import (
    create_account,
    delete_account,
    list_accounts,
    list_accounts_selection,
    update_account,
)

router = APIRouter(prefix="/accounts", tags=["settings:accounts"])


@router.get(
    "",
    summary="List accounts",
    description="List accounts with optional filters on name, account_type, in_use.",
    response_model=ApiResponse[list[AccountRead]],
    responses={422: VALIDATION_ERROR, 500: INTERNAL_ERROR},
)
def list_accounts_endpoint(
    name: Annotated[str | None, Query(description="Name substring filter", examples=["Bank"])] = None,
    account_type: Annotated[str | None, Query(description="Account type filter", examples=["bank"])] = None,
    in_use: Annotated[str | None, Query(description="In-use flag filter", examples=["Y"])] = None,
    session: Session = Depends(get_session),
) -> ApiResponse[list[AccountRead]]:
    rows = list_accounts(session, name=name, account_type=account_type, in_use=in_use)
    return ApiResponse(data=[AccountRead.model_validate(r, from_attributes=True) for r in rows])


@router.get(
    "/selection",
    summary="Active accounts for dropdown",
    description="Return in-use accounts ordered by account_index ASC for use in dropdowns.",
    response_model=ApiResponse[list[AccountRead]],
    responses={422: VALIDATION_ERROR, 500: INTERNAL_ERROR},
)
def list_accounts_selection_endpoint(
    session: Session = Depends(get_session),
) -> ApiResponse[list[AccountRead]]:
    rows = list_accounts_selection(session)
    return ApiResponse(data=[AccountRead.model_validate(r, from_attributes=True) for r in rows])


@router.post(
    "",
    summary="Create account",
    description=(
        "Create an account. Rejects 422 when account_id is missing; "
        "409 when account_id duplicates existing row."
    ),
    response_model=ApiResponse[AccountRead],
    responses={
        409: error_response(
            "Duplicate account_id",
            error_payload="Account with account_id 'BANK-CHASE-01' already exists",
        ),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def create_account_endpoint(
    payload: AccountCreate,
    session: Session = Depends(get_session),
) -> ApiResponse[AccountRead]:
    account = create_account(session, payload)
    return ApiResponse(data=AccountRead.model_validate(account, from_attributes=True))


@router.put(
    "/{id}",
    summary="Update account",
    description="Update an account by autoincrement id. Returns 404 if id not found.",
    response_model=ApiResponse[AccountRead],
    responses={
        404: not_found_error("Account"),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def update_account_endpoint(
    id: int,
    payload: AccountUpdate,
    session: Session = Depends(get_session),
) -> ApiResponse[AccountRead]:
    account = update_account(session, id, payload)
    return ApiResponse(data=AccountRead.model_validate(account, from_attributes=True))


@router.delete(
    "/{id}",
    summary="Delete account",
    description="Delete an account by autoincrement id. Returns 404 if id not found.",
    response_model=ApiResponse[dict],
    responses={422: VALIDATION_ERROR, 404: not_found_error("Account"), 500: INTERNAL_ERROR},
)
def delete_account_endpoint(
    id: int,
    session: Session = Depends(get_session),
) -> ApiResponse[dict]:
    delete_account(session, id)
    return ApiResponse(data={"id": id})
