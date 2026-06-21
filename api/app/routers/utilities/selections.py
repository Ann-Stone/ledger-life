"""Utility selection endpoints (dropdown helpers)."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlmodel import Session

from app.database import get_session
from app.models.utilities.selection import SelectionGroup
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    error_response,
)
from app.services.utility_service import (
    get_account_selection_groups,
    get_code_selection_groups,
    get_credit_card_selection_groups,
    get_estate_selection_groups,
    get_insurance_selection_groups,
    get_loan_selection_groups,
    get_other_asset_type_selection_groups,
    get_stock_category_selection_groups,
    get_stock_selection_groups,
    get_sub_code_selection_groups,
)

router = APIRouter(prefix="/selections", tags=["utilities:selections"])

_COMMON_RESPONSES = {500: INTERNAL_ERROR}


@router.get(
    "/accounts",
    summary="List accounts grouped by type",
    description="Return active accounts grouped by account_type, ordered by account_index ASC.",
    response_model=ApiResponse[list[SelectionGroup]],
    responses=_COMMON_RESPONSES,
)
def list_account_selections(
    session: Session = Depends(get_session),
) -> ApiResponse[list[SelectionGroup]]:
    return ApiResponse(data=get_account_selection_groups(session))


@router.get(
    "/credit-cards",
    summary="List credit cards as a single group",
    description="Return active credit cards in one group labelled 'Credit_Card'.",
    response_model=ApiResponse[list[SelectionGroup]],
    responses=_COMMON_RESPONSES,
)
def list_credit_card_selections(
    session: Session = Depends(get_session),
) -> ApiResponse[list[SelectionGroup]]:
    return ApiResponse(data=get_credit_card_selection_groups(session))


@router.get(
    "/loans",
    summary="List loans as a single group",
    description="Return loans in one group labelled 'Loan'.",
    response_model=ApiResponse[list[SelectionGroup]],
    responses=_COMMON_RESPONSES,
)
def list_loan_selections(
    session: Session = Depends(get_session),
) -> ApiResponse[list[SelectionGroup]]:
    return ApiResponse(data=get_loan_selection_groups(session))


@router.get(
    "/other-asset-types",
    summary="List distinct asset_type values from Other_Asset",
    description=(
        "Return one group whose options are the distinct asset_type values "
        "across active Other_Asset rows. Drives the 'transfer to other asset' "
        "sub-category dropdown so it stays in sync with the user's asset setup."
    ),
    response_model=ApiResponse[list[SelectionGroup]],
    responses=_COMMON_RESPONSES,
)
def list_other_asset_type_selections(
    session: Session = Depends(get_session),
) -> ApiResponse[list[SelectionGroup]]:
    return ApiResponse(data=get_other_asset_type_selection_groups(session))


@router.get(
    "/stocks",
    summary="List stock holdings grouped by asset_id",
    description=(
        "Return every Stock_Journal row grouped by its parent asset_id; each "
        "option's label is '<stock_code> <stock_name>' for filterable dropdowns."
    ),
    response_model=ApiResponse[list[SelectionGroup]],
    responses=_COMMON_RESPONSES,
)
def list_stock_selections(
    session: Session = Depends(get_session),
) -> ApiResponse[list[SelectionGroup]]:
    return ApiResponse(data=get_stock_selection_groups(session))


@router.get(
    "/stock-categories",
    summary="List active stock categories as a single group",
    description=(
        "Return active (in_use='Y') stock allocation categories in one group "
        "labelled 'Stock_Category', ordered by category_index. Drives the "
        "allocation-category dropdown on the stock holding form."
    ),
    response_model=ApiResponse[list[SelectionGroup]],
    responses=_COMMON_RESPONSES,
)
def list_stock_category_selections(
    session: Session = Depends(get_session),
) -> ApiResponse[list[SelectionGroup]]:
    return ApiResponse(data=get_stock_category_selection_groups(session))


@router.get(
    "/insurances",
    summary="List insurance policies as a single group",
    description="Return open insurance policies (has_closed != 'Y') in one group labelled 'Insurance'.",
    response_model=ApiResponse[list[SelectionGroup]],
    responses=_COMMON_RESPONSES,
)
def list_insurance_selections(
    session: Session = Depends(get_session),
) -> ApiResponse[list[SelectionGroup]]:
    return ApiResponse(data=get_insurance_selection_groups(session))


@router.get(
    "/estates",
    summary="List estates as a single group",
    description="Return active estates (estate_status != 'sold') in one group labelled 'Estate'.",
    response_model=ApiResponse[list[SelectionGroup]],
    responses=_COMMON_RESPONSES,
)
def list_estate_selections(
    session: Session = Depends(get_session),
) -> ApiResponse[list[SelectionGroup]]:
    return ApiResponse(data=get_estate_selection_groups(session))


@router.get(
    "/codes",
    summary="List top-level codes grouped by code_type",
    description="Return codes whose parent_id is NULL, grouped by code_type and ordered by code_index ASC.",
    response_model=ApiResponse[list[SelectionGroup]],
    responses=_COMMON_RESPONSES,
)
def list_code_selections(
    session: Session = Depends(get_session),
) -> ApiResponse[list[SelectionGroup]]:
    return ApiResponse(data=get_code_selection_groups(session))


@router.get(
    "/codes/{parent_id}",
    summary="List sub-codes for a parent code",
    description="Return children of the parent code (parent_id) as a single 'sub' group.",
    response_model=ApiResponse[list[SelectionGroup]],
    responses={
        **_COMMON_RESPONSES,
        422: VALIDATION_ERROR,
        404: error_response(
            "Parent code has no children",
            error_payload="Parent code 'XYZ' has no children",
        ),
    },
)
def list_sub_code_selections(
    parent_id: Annotated[
        str,
        Path(..., description="Parent code_id", examples=["92"]),
    ],
    session: Session = Depends(get_session),
) -> ApiResponse[list[SelectionGroup]]:
    return ApiResponse(data=get_sub_code_selection_groups(session, parent_id))
