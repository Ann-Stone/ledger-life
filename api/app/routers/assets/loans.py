"""Loan / Liability CRUD + transaction detail endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.models.assets.loan import (
    LoanCreate,
    LoanJournalCreate,
    LoanJournalRead,
    LoanJournalUpdate,
    LoanRead,
    LoanSelectionRead,
    LoanUpdate,
)
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    error_response,
    not_found_error,
)
from app.services.asset_service import (
    create_loan,
    create_loan_detail,
    delete_loan,
    delete_loan_detail,
    get_loan,
    list_loan_details,
    list_loan_selection,
    list_loans,
    update_loan,
    update_loan_detail,
)

router = APIRouter()


@router.get(
    "",
    summary="List loans",
    description="Return all loan liabilities ordered by loan_index.",
    response_model=ApiResponse[list[LoanRead]],
    responses={422: VALIDATION_ERROR, 500: INTERNAL_ERROR},
)
def list_loans_endpoint(
    session: Session = Depends(get_session),
) -> ApiResponse[list[LoanRead]]:
    rows = list_loans(session)
    return ApiResponse(data=[LoanRead.model_validate(r, from_attributes=True) for r in rows])


@router.get(
    "/selection",
    summary="Loan dropdown options",
    description="Return id/name pairs for loan selection UIs.",
    response_model=ApiResponse[list[LoanSelectionRead]],
    responses={422: VALIDATION_ERROR, 500: INTERNAL_ERROR},
)
def loan_selection_endpoint(
    session: Session = Depends(get_session),
) -> ApiResponse[list[LoanSelectionRead]]:
    rows = list_loan_selection(session)
    return ApiResponse(data=rows)


@router.post(
    "",
    summary="Create loan",
    description="Create a new loan liability; dates accept ISO 8601 and are stored as YYYYMMDD.",
    response_model=ApiResponse[LoanRead],
    responses={
        409: error_response("Duplicate loan_id", error_payload="Duplicate loan_id"),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def create_loan_endpoint(
    payload: LoanCreate, session: Session = Depends(get_session)
) -> ApiResponse[LoanRead]:
    row = create_loan(session, payload)
    return ApiResponse(data=LoanRead.model_validate(row, from_attributes=True))


@router.get(
    "/{loan_id}",
    summary="Get loan",
    description="Return a single loan by id.",
    response_model=ApiResponse[LoanRead],
    responses={
        422: VALIDATION_ERROR,
        404: not_found_error("Loan"),
        500: INTERNAL_ERROR,
    },
)
def get_loan_endpoint(
    loan_id: str, session: Session = Depends(get_session)
) -> ApiResponse[LoanRead]:
    row = get_loan(session, loan_id)
    return ApiResponse(data=LoanRead.model_validate(row, from_attributes=True))


@router.put(
    "/{loan_id}",
    summary="Update loan",
    description="Update a loan; repayed is server-computed and cannot be set via this endpoint.",
    response_model=ApiResponse[LoanRead],
    responses={
        422: VALIDATION_ERROR,
        404: not_found_error("Loan"),
        500: INTERNAL_ERROR,
    },
)
def update_loan_endpoint(
    loan_id: str,
    payload: LoanUpdate,
    session: Session = Depends(get_session),
) -> ApiResponse[LoanRead]:
    row = update_loan(session, loan_id, payload)
    return ApiResponse(data=LoanRead.model_validate(row, from_attributes=True))


@router.delete(
    "/{loan_id}",
    summary="Delete loan",
    description="Delete a loan by id.",
    response_model=ApiResponse[dict],
    responses={
        422: VALIDATION_ERROR,
        404: not_found_error("Loan"),
        500: INTERNAL_ERROR,
    },
)
def delete_loan_endpoint(
    loan_id: str, session: Session = Depends(get_session)
) -> ApiResponse[dict]:
    delete_loan(session, loan_id)
    return ApiResponse(data={"loan_id": loan_id})


@router.get(
    "/{loan_id}/details",
    summary="List loan transactions",
    description="Return all repayment / interest / fee / increment transactions for a loan.",
    response_model=ApiResponse[list[LoanJournalRead]],
    responses={
        422: VALIDATION_ERROR,
        404: not_found_error("Loan"),
        500: INTERNAL_ERROR,
    },
)
def list_loan_details_endpoint(
    loan_id: str, session: Session = Depends(get_session)
) -> ApiResponse[list[LoanJournalRead]]:
    rows = list_loan_details(session, loan_id)
    return ApiResponse(data=[LoanJournalRead.model_validate(r, from_attributes=True) for r in rows])


@router.post(
    "/{loan_id}/details",
    summary="Record loan transaction",
    description="Record a principal/interest/increment/fee transaction. Server auto-recalculates Loan.repayed on principal rows.",
    response_model=ApiResponse[LoanJournalRead],
    responses={
        404: not_found_error("Loan"),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def create_loan_detail_endpoint(
    loan_id: str,
    payload: LoanJournalCreate,
    session: Session = Depends(get_session),
) -> ApiResponse[LoanJournalRead]:
    row = create_loan_detail(session, loan_id, payload)
    return ApiResponse(data=LoanJournalRead.model_validate(row, from_attributes=True))


@router.put(
    "/details/{distinct_number}",
    summary="Update loan transaction",
    description="Update a single loan transaction row; Loan.repayed auto-recalculates.",
    response_model=ApiResponse[LoanJournalRead],
    responses={
        422: VALIDATION_ERROR,
        404: error_response("Transaction not found", error_payload="Transaction not found"),
        500: INTERNAL_ERROR,
    },
)
def update_loan_detail_endpoint(
    distinct_number: int,
    payload: LoanJournalUpdate,
    session: Session = Depends(get_session),
) -> ApiResponse[LoanJournalRead]:
    row = update_loan_detail(session, distinct_number, payload)
    return ApiResponse(data=LoanJournalRead.model_validate(row, from_attributes=True))


@router.delete(
    "/details/{distinct_number}",
    summary="Delete loan transaction",
    description="Delete a single loan transaction row; Loan.repayed auto-recalculates.",
    response_model=ApiResponse[dict],
    responses={
        422: VALIDATION_ERROR,
        404: error_response("Transaction not found", error_payload="Transaction not found"),
        500: INTERNAL_ERROR,
    },
)
def delete_loan_detail_endpoint(
    distinct_number: int, session: Session = Depends(get_session)
) -> ApiResponse[dict]:
    delete_loan_detail(session, distinct_number)
    return ApiResponse(data={"distinct_number": distinct_number})
