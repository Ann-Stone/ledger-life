"""Stock asset CRUD + transaction detail endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.models.assets.stock import (
    StockDetailCreate,
    StockDetailRead,
    StockDetailUpdate,
    StockJournalCreate,
    StockJournalRead,
    StockJournalUpdate,
    StockPnlSummaryRead,
)
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    error_response,
    not_found_error,
)
from app.services.asset_service import (
    create_stock,
    create_stock_detail,
    delete_stock,
    delete_stock_detail,
    list_stock_details,
    list_stocks,
    update_stock,
    update_stock_detail,
)
from app.services.stock_service import compute_stock_pnl_summary

router = APIRouter()


@router.get(
    "",
    summary="List stock holdings",
    description="Return stock holdings filtered by asset_id.",
    response_model=ApiResponse[list[StockJournalRead]],
    responses={
        422: VALIDATION_ERROR,
        400: error_response("Invalid query", error_payload="Invalid query"),
        500: INTERNAL_ERROR,
    },
)
def list_stocks_endpoint(
    asset_id: Annotated[str, Query(..., description="Parent asset category id", examples=["AC-STK-001"])],
    session: Session = Depends(get_session),
) -> ApiResponse[list[StockJournalRead]]:
    rows = list_stocks(session, asset_id=asset_id)
    return ApiResponse(data=[StockJournalRead.model_validate(r, from_attributes=True) for r in rows])


@router.get(
    "/summary",
    summary="Per-stock P&L summary",
    description=(
        "Computed per-holding performance for an asset category: moving-average "
        "cost, latest market value, realized gain (capital gains, dividends "
        "excluded), cumulative dividends, unrealized gain/%, and trailing-12m "
        "cash yield / cost yield. Figures are in each holding's own currency. "
        "Derived fresh from Stock_Detail (the only per-stock source)."
    ),
    response_model=ApiResponse[list[StockPnlSummaryRead]],
    responses={
        422: VALIDATION_ERROR,
        400: error_response("Invalid query", error_payload="Invalid query"),
        500: INTERNAL_ERROR,
    },
)
def stock_pnl_summary_endpoint(
    asset_id: Annotated[str, Query(..., description="Parent asset category id", examples=["AC-STK-001"])],
    as_of_month: Annotated[
        str | None,
        Query(
            description="Valuation month as YYYYMM; defaults to the current month.",
            examples=["202606"],
        ),
    ] = None,
    session: Session = Depends(get_session),
) -> ApiResponse[list[StockPnlSummaryRead]]:
    month = as_of_month or datetime.now().strftime("%Y%m")
    rows = compute_stock_pnl_summary(session, asset_id=asset_id, as_of_month=month)
    return ApiResponse(data=rows)


@router.post(
    "",
    summary="Create stock holding",
    description="Create a new stock holding under an asset category.",
    response_model=ApiResponse[StockJournalRead],
    responses={
        409: error_response("Duplicate stock_id", error_payload="Duplicate stock_id"),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def create_stock_endpoint(
    payload: StockJournalCreate,
    session: Session = Depends(get_session),
) -> ApiResponse[StockJournalRead]:
    row = create_stock(session, payload)
    return ApiResponse(data=StockJournalRead.model_validate(row, from_attributes=True))


@router.put(
    "/{stock_id}",
    summary="Update stock holding",
    description="Update a stock holding by id; any omitted field is left unchanged.",
    response_model=ApiResponse[StockJournalRead],
    responses={
        422: VALIDATION_ERROR,
        404: not_found_error("Stock"),
        500: INTERNAL_ERROR,
    },
)
def update_stock_endpoint(
    stock_id: str,
    payload: StockJournalUpdate,
    session: Session = Depends(get_session),
) -> ApiResponse[StockJournalRead]:
    row = update_stock(session, stock_id, payload)
    return ApiResponse(data=StockJournalRead.model_validate(row, from_attributes=True))


@router.delete(
    "/{stock_id}",
    summary="Delete stock holding",
    description="Delete a stock holding by id.",
    response_model=ApiResponse[dict],
    responses={
        422: VALIDATION_ERROR,
        404: not_found_error("Stock"),
        500: INTERNAL_ERROR,
    },
)
def delete_stock_endpoint(
    stock_id: str,
    session: Session = Depends(get_session),
) -> ApiResponse[dict]:
    delete_stock(session, stock_id)
    return ApiResponse(data={"stock_id": stock_id})


@router.get(
    "/{stock_id}/details",
    summary="List stock transactions",
    description="Return all buy/sell/stock-dividend/cash-dividend transactions for a holding.",
    response_model=ApiResponse[list[StockDetailRead]],
    responses={
        422: VALIDATION_ERROR,
        404: not_found_error("Stock"),
        500: INTERNAL_ERROR,
    },
)
def list_stock_details_endpoint(
    stock_id: str,
    session: Session = Depends(get_session),
) -> ApiResponse[list[StockDetailRead]]:
    rows = list_stock_details(session, stock_id)
    return ApiResponse(data=[StockDetailRead.model_validate(r, from_attributes=True) for r in rows])


@router.post(
    "/{stock_id}/details",
    summary="Record stock transaction",
    description="Record a buy/sell/stock-dividend/cash-dividend transaction.",
    response_model=ApiResponse[StockDetailRead],
    responses={
        404: not_found_error("Stock"),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def create_stock_detail_endpoint(
    stock_id: str,
    payload: StockDetailCreate,
    session: Session = Depends(get_session),
) -> ApiResponse[StockDetailRead]:
    row = create_stock_detail(session, stock_id, payload)
    return ApiResponse(data=StockDetailRead.model_validate(row, from_attributes=True))


@router.put(
    "/details/{distinct_number}",
    summary="Update stock transaction",
    description="Update a single stock transaction row.",
    response_model=ApiResponse[StockDetailRead],
    responses={
        422: VALIDATION_ERROR,
        404: error_response("Transaction not found", error_payload="Transaction not found"),
        500: INTERNAL_ERROR,
    },
)
def update_stock_detail_endpoint(
    distinct_number: int,
    payload: StockDetailUpdate,
    session: Session = Depends(get_session),
) -> ApiResponse[StockDetailRead]:
    row = update_stock_detail(session, distinct_number, payload)
    return ApiResponse(data=StockDetailRead.model_validate(row, from_attributes=True))


@router.delete(
    "/details/{distinct_number}",
    summary="Delete stock transaction",
    description="Delete a single stock transaction row.",
    response_model=ApiResponse[dict],
    responses={
        422: VALIDATION_ERROR,
        404: error_response("Transaction not found", error_payload="Transaction not found"),
        500: INTERNAL_ERROR,
    },
)
def delete_stock_detail_endpoint(
    distinct_number: int,
    session: Session = Depends(get_session),
) -> ApiResponse[dict]:
    delete_stock_detail(session, distinct_number)
    return ApiResponse(data={"distinct_number": distinct_number})
