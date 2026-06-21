"""Insurance asset CRUD + transaction detail endpoints."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.models.assets.insurance import (
    InsuranceCreate,
    InsuranceJournalCreate,
    InsuranceJournalRead,
    InsuranceJournalUpdate,
    InsuranceRead,
    InsuranceUpdate,
)
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    error_response,
    not_found_error,
)
from app.services.asset_service import (
    create_insurance,
    create_insurance_detail,
    delete_insurance,
    delete_insurance_detail,
    list_insurance_details,
    list_insurances,
    update_insurance,
    update_insurance_detail,
)

router = APIRouter()


@router.get(
    "",
    summary="List insurance policies",
    description="Return policies under a given asset_id.",
    response_model=ApiResponse[list[InsuranceRead]],
    responses={
        422: VALIDATION_ERROR,
        400: error_response("Invalid query", error_payload="Invalid query"),
        500: INTERNAL_ERROR,
    },
)
def list_insurances_endpoint(
    asset_id: Annotated[str, Query(..., description="Parent asset category id", examples=["AC-INS-001"])],
    session: Session = Depends(get_session),
) -> ApiResponse[list[InsuranceRead]]:
    rows = list_insurances(session, asset_id=asset_id)
    return ApiResponse(data=[InsuranceRead.model_validate(r, from_attributes=True) for r in rows])


@router.post(
    "",
    summary="Create insurance policy",
    description="Create a policy; start/end dates accept ISO 8601 and are stored as YYYYMMDD.",
    response_model=ApiResponse[InsuranceRead],
    responses={
        409: error_response("Duplicate insurance_id", error_payload="Duplicate insurance_id"),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def create_insurance_endpoint(
    payload: InsuranceCreate, session: Session = Depends(get_session)
) -> ApiResponse[InsuranceRead]:
    row = create_insurance(session, payload)
    return ApiResponse(data=InsuranceRead.model_validate(row, from_attributes=True))


@router.put(
    "/{insurance_id}",
    summary="Update insurance policy",
    description="Update a policy by id; any omitted field is left unchanged.",
    response_model=ApiResponse[InsuranceRead],
    responses={
        422: VALIDATION_ERROR,
        404: not_found_error("Insurance"),
        500: INTERNAL_ERROR,
    },
)
def update_insurance_endpoint(
    insurance_id: str,
    payload: InsuranceUpdate,
    session: Session = Depends(get_session),
) -> ApiResponse[InsuranceRead]:
    row = update_insurance(session, insurance_id, payload)
    return ApiResponse(data=InsuranceRead.model_validate(row, from_attributes=True))


@router.delete(
    "/{insurance_id}",
    summary="Delete insurance policy",
    description="Delete a policy by id.",
    response_model=ApiResponse[dict],
    responses={
        422: VALIDATION_ERROR,
        404: not_found_error("Insurance"),
        500: INTERNAL_ERROR,
    },
)
def delete_insurance_endpoint(
    insurance_id: str, session: Session = Depends(get_session)
) -> ApiResponse[dict]:
    delete_insurance(session, insurance_id)
    return ApiResponse(data={"insurance_id": insurance_id})


@router.get(
    "/{insurance_id}/details",
    summary="List insurance transactions",
    description="Return all premium/claim/return transactions for a policy.",
    response_model=ApiResponse[list[InsuranceJournalRead]],
    responses={
        422: VALIDATION_ERROR,
        404: not_found_error("Insurance"),
        500: INTERNAL_ERROR,
    },
)
def list_insurance_details_endpoint(
    insurance_id: str, session: Session = Depends(get_session)
) -> ApiResponse[list[InsuranceJournalRead]]:
    rows = list_insurance_details(session, insurance_id)
    return ApiResponse(data=[InsuranceJournalRead.model_validate(r, from_attributes=True) for r in rows])


@router.post(
    "/{insurance_id}/details",
    summary="Record insurance premium/claim",
    description="Record a pay/cash/return/expect transaction.",
    response_model=ApiResponse[InsuranceJournalRead],
    responses={
        404: not_found_error("Insurance"),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def create_insurance_detail_endpoint(
    insurance_id: str,
    payload: InsuranceJournalCreate,
    session: Session = Depends(get_session),
) -> ApiResponse[InsuranceJournalRead]:
    row = create_insurance_detail(session, insurance_id, payload)
    return ApiResponse(data=InsuranceJournalRead.model_validate(row, from_attributes=True))


@router.put(
    "/details/{distinct_number}",
    summary="Update insurance transaction",
    description="Update a single insurance transaction row.",
    response_model=ApiResponse[InsuranceJournalRead],
    responses={
        422: VALIDATION_ERROR,
        404: error_response("Transaction not found", error_payload="Transaction not found"),
        500: INTERNAL_ERROR,
    },
)
def update_insurance_detail_endpoint(
    distinct_number: int,
    payload: InsuranceJournalUpdate,
    session: Session = Depends(get_session),
) -> ApiResponse[InsuranceJournalRead]:
    row = update_insurance_detail(session, distinct_number, payload)
    return ApiResponse(data=InsuranceJournalRead.model_validate(row, from_attributes=True))


@router.delete(
    "/details/{distinct_number}",
    summary="Delete insurance transaction",
    description="Delete a single insurance transaction row.",
    response_model=ApiResponse[dict],
    responses={
        422: VALIDATION_ERROR,
        404: error_response("Transaction not found", error_payload="Transaction not found"),
        500: INTERNAL_ERROR,
    },
)
def delete_insurance_detail_endpoint(
    distinct_number: int, session: Session = Depends(get_session)
) -> ApiResponse[dict]:
    delete_insurance_detail(session, distinct_number)
    return ApiResponse(data={"distinct_number": distinct_number})
