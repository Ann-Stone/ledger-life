"""Credit card endpoints (Settings domain)."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.models.settings.credit_card import (
    CreditCardCreate,
    CreditCardRead,
    CreditCardUpdate,
)
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    error_response,
    not_found_error,
)
from app.services.setting_service import (
    create_credit_card,
    delete_credit_card,
    list_credit_cards,
    update_credit_card,
)

router = APIRouter(prefix="/credit-cards", tags=["settings:credit-cards"])


@router.get(
    "",
    summary="List credit cards",
    description=(
        "List credit cards with optional filters on card_name (substring) "
        "and in_use. Ordered by credit_card_index ASC."
    ),
    response_model=ApiResponse[list[CreditCardRead]],
    responses={
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def list_credit_cards_endpoint(
    card_name: Annotated[
        str | None,
        Query(description="Card name substring filter", examples=["Cathay"]),
    ] = None,
    in_use: Annotated[
        str | None,
        Query(description="Active flag filter Y/N", examples=["Y"]),
    ] = None,
    session: Session = Depends(get_session),
) -> ApiResponse[list[CreditCardRead]]:
    rows = list_credit_cards(session, card_name=card_name, in_use=in_use)
    return ApiResponse(
        data=[CreditCardRead.model_validate(r, from_attributes=True) for r in rows]
    )


@router.post(
    "",
    summary="Create credit card",
    description=(
        "Create a credit card. When credit_card_index is omitted, "
        "auto-fill with max(credit_card_index)+1."
    ),
    response_model=ApiResponse[CreditCardRead],
    responses={
        409: error_response("Duplicate credit_card_id", error_payload="Duplicate credit_card_id"),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def create_credit_card_endpoint(
    payload: CreditCardCreate,
    session: Session = Depends(get_session),
) -> ApiResponse[CreditCardRead]:
    card = create_credit_card(session, payload)
    return ApiResponse(data=CreditCardRead.model_validate(card, from_attributes=True))


@router.put(
    "/{credit_card_id}",
    summary="Update credit card",
    description="Update a credit card by credit_card_id. Returns 404 if not found.",
    response_model=ApiResponse[CreditCardRead],
    responses={
        404: not_found_error("Credit card"),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def update_credit_card_endpoint(
    credit_card_id: str,
    payload: CreditCardUpdate,
    session: Session = Depends(get_session),
) -> ApiResponse[CreditCardRead]:
    card = update_credit_card(session, credit_card_id, payload)
    return ApiResponse(data=CreditCardRead.model_validate(card, from_attributes=True))


@router.delete(
    "/{credit_card_id}",
    summary="Delete credit card",
    description="Delete a credit card by credit_card_id. Returns 404 if not found.",
    response_model=ApiResponse[dict],
    responses={
        422: VALIDATION_ERROR,
        404: not_found_error("Credit card"),
        500: INTERNAL_ERROR,
    },
)
def delete_credit_card_endpoint(
    credit_card_id: str,
    session: Session = Depends(get_session),
) -> ApiResponse[dict]:
    delete_credit_card(session, credit_card_id)
    return ApiResponse(data={"credit_card_id": credit_card_id})
