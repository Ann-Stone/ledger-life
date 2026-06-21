"""Stock category dictionary CRUD endpoints (Settings domain).

Maintains the user-defined stock allocation classes referenced by
``Stock_Journal.category_id``. Sits alongside the other dictionary maintenance
endpoints (codes, accounts) even though the entity belongs to the Assets domain.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.models.assets.stock_category import (
    StockCategoryCreate,
    StockCategoryRead,
    StockCategoryUpdate,
)
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    error_response,
    not_found_error,
)
from app.services.stock_category_service import (
    create_stock_category,
    delete_stock_category,
    list_stock_categories,
    update_stock_category,
)

router = APIRouter(prefix="/stock-categories", tags=["settings:stock-categories"])


@router.get(
    "",
    summary="List stock categories",
    description="List stock allocation categories ordered by category_index.",
    response_model=ApiResponse[list[StockCategoryRead]],
    responses={422: VALIDATION_ERROR, 500: INTERNAL_ERROR},
)
def list_stock_categories_endpoint(
    session: Session = Depends(get_session),
) -> ApiResponse[list[StockCategoryRead]]:
    rows = list_stock_categories(session)
    return ApiResponse(data=[StockCategoryRead.model_validate(r, from_attributes=True) for r in rows])


@router.post(
    "",
    summary="Create stock category",
    description="Create a stock category. The category_id is generated server-side (SC-NNN).",
    response_model=ApiResponse[StockCategoryRead],
    responses={422: VALIDATION_ERROR, 500: INTERNAL_ERROR},
)
def create_stock_category_endpoint(
    payload: StockCategoryCreate,
    session: Session = Depends(get_session),
) -> ApiResponse[StockCategoryRead]:
    row = create_stock_category(session, payload)
    return ApiResponse(data=StockCategoryRead.model_validate(row, from_attributes=True))


@router.put(
    "/{category_id}",
    summary="Update stock category",
    description="Update a stock category by id. Set in_use='N' to retire it. Returns 404 if not found.",
    response_model=ApiResponse[StockCategoryRead],
    responses={404: not_found_error("Stock category"), 422: VALIDATION_ERROR, 500: INTERNAL_ERROR},
)
def update_stock_category_endpoint(
    category_id: str,
    payload: StockCategoryUpdate,
    session: Session = Depends(get_session),
) -> ApiResponse[StockCategoryRead]:
    row = update_stock_category(session, category_id, payload)
    return ApiResponse(data=StockCategoryRead.model_validate(row, from_attributes=True))


@router.delete(
    "/{category_id}",
    summary="Delete stock category",
    description=(
        "Delete a stock category by id. Refused with 409 when any holding still "
        "references it — retire it with in_use='N' instead."
    ),
    response_model=ApiResponse[dict],
    responses={
        404: not_found_error("Stock category"),
        409: error_response(
            "Category in use",
            error_payload="Stock category SC-001 is in use by one or more holdings",
        ),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def delete_stock_category_endpoint(
    category_id: str,
    session: Session = Depends(get_session),
) -> ApiResponse[dict]:
    delete_stock_category(session, category_id)
    return ApiResponse(data={"category_id": category_id})
