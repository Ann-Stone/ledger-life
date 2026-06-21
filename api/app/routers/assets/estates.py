"""Real-Estate asset CRUD + transaction detail endpoints."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.models.assets.estate import (
    EstateCreate,
    EstateJournalCreate,
    EstateJournalRead,
    EstateJournalUpdate,
    EstateRead,
    EstateUpdate,
)
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    error_response,
    not_found_error,
)
from app.services.asset_service import (
    create_estate,
    create_estate_detail,
    delete_estate,
    delete_estate_detail,
    list_estate_details,
    list_estates,
    update_estate,
    update_estate_detail,
)

router = APIRouter()


@router.get(
    "",
    summary="List real-estate holdings",
    description="Return estate properties filtered by asset_id.",
    response_model=ApiResponse[list[EstateRead]],
    responses={
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def list_estates_endpoint(
    asset_id: Annotated[str, Query(..., description="Parent asset category id", examples=["AC-REAL-001"])],
    session: Session = Depends(get_session),
) -> ApiResponse[list[EstateRead]]:
    rows = list_estates(session, asset_id=asset_id)
    return ApiResponse(data=[EstateRead.model_validate(r, from_attributes=True) for r in rows])


@router.post(
    "",
    summary="Create real-estate holding",
    description="Create a new estate property; obtain_date accepts ISO 8601 and is stored as YYYYMMDD.",
    response_model=ApiResponse[EstateRead],
    responses={
        409: error_response("Duplicate estate_id", error_payload="Duplicate estate_id"),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def create_estate_endpoint(
    payload: EstateCreate, session: Session = Depends(get_session)
) -> ApiResponse[EstateRead]:
    row = create_estate(session, payload)
    return ApiResponse(data=EstateRead.model_validate(row, from_attributes=True))


@router.put(
    "/{estate_id}",
    summary="Update real-estate holding",
    description="Update an estate property; any omitted field is left unchanged.",
    response_model=ApiResponse[EstateRead],
    responses={
        422: VALIDATION_ERROR,
        404: not_found_error("Estate"),
        500: INTERNAL_ERROR,
    },
)
def update_estate_endpoint(
    estate_id: str,
    payload: EstateUpdate,
    session: Session = Depends(get_session),
) -> ApiResponse[EstateRead]:
    row = update_estate(session, estate_id, payload)
    return ApiResponse(data=EstateRead.model_validate(row, from_attributes=True))


@router.delete(
    "/{estate_id}",
    summary="Delete real-estate holding",
    description="Delete an estate property by id.",
    response_model=ApiResponse[dict],
    responses={
        422: VALIDATION_ERROR,
        404: not_found_error("Estate"),
        500: INTERNAL_ERROR,
    },
)
def delete_estate_endpoint(
    estate_id: str, session: Session = Depends(get_session)
) -> ApiResponse[dict]:
    delete_estate(session, estate_id)
    return ApiResponse(data={"estate_id": estate_id})


@router.get(
    "/{estate_id}/details",
    summary="List estate transactions",
    description="Return all fee/tax/rent/deposit transactions for an estate property.",
    response_model=ApiResponse[list[EstateJournalRead]],
    responses={
        422: VALIDATION_ERROR,
        404: not_found_error("Estate"),
        500: INTERNAL_ERROR,
    },
)
def list_estate_details_endpoint(
    estate_id: str, session: Session = Depends(get_session)
) -> ApiResponse[list[EstateJournalRead]]:
    rows = list_estate_details(session, estate_id)
    return ApiResponse(data=[EstateJournalRead.model_validate(r, from_attributes=True) for r in rows])


@router.post(
    "/{estate_id}/details",
    summary="Record estate transaction",
    description="Record a tax/fee/insurance/fix/rent/deposit transaction.",
    response_model=ApiResponse[EstateJournalRead],
    responses={
        404: not_found_error("Estate"),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def create_estate_detail_endpoint(
    estate_id: str,
    payload: EstateJournalCreate,
    session: Session = Depends(get_session),
) -> ApiResponse[EstateJournalRead]:
    row = create_estate_detail(session, estate_id, payload)
    return ApiResponse(data=EstateJournalRead.model_validate(row, from_attributes=True))


@router.put(
    "/details/{distinct_number}",
    summary="Update estate transaction",
    description="Update a single estate transaction row.",
    response_model=ApiResponse[EstateJournalRead],
    responses={
        422: VALIDATION_ERROR,
        404: error_response("Transaction not found", error_payload="Transaction not found"),
        500: INTERNAL_ERROR,
    },
)
def update_estate_detail_endpoint(
    distinct_number: int,
    payload: EstateJournalUpdate,
    session: Session = Depends(get_session),
) -> ApiResponse[EstateJournalRead]:
    row = update_estate_detail(session, distinct_number, payload)
    return ApiResponse(data=EstateJournalRead.model_validate(row, from_attributes=True))


@router.delete(
    "/details/{distinct_number}",
    summary="Delete estate transaction",
    description="Delete a single estate transaction row.",
    response_model=ApiResponse[dict],
    responses={
        422: VALIDATION_ERROR,
        404: error_response("Transaction not found", error_payload="Transaction not found"),
        500: INTERNAL_ERROR,
    },
)
def delete_estate_detail_endpoint(
    distinct_number: int, session: Session = Depends(get_session)
) -> ApiResponse[dict]:
    delete_estate_detail(session, distinct_number)
    return ApiResponse(data={"distinct_number": distinct_number})
