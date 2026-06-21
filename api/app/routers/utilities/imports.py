"""Data import endpoints: stock prices, FX rates, invoice CSV."""
from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, File, UploadFile

from app.models.utilities.imports import (
    ImportAcceptedResponse,
    ImportRequest,
    InvoiceImportResult,
)
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
)
from app.services.import_service import (
    import_fx_rates,
    import_invoices,
    import_stock_prices,
)

router = APIRouter(prefix="/import", tags=["utilities:imports"])

_ACCEPTED_RESPONSES = {
    422: VALIDATION_ERROR,
    500: INTERNAL_ERROR,
}


@router.post(
    "/stock-prices",
    summary="Fetch stock prices via yfinance",
    description=(
        "Kicks off a background task that pulls daily OHLC for every distinct "
        "ticker in StockJournal and upserts into Stock_Price_History."
    ),
    response_model=ApiResponse[ImportAcceptedResponse],
    responses=_ACCEPTED_RESPONSES,
    status_code=202,
)
def trigger_stock_import(
    body: ImportRequest, tasks: BackgroundTasks
) -> ApiResponse[ImportAcceptedResponse]:
    tasks.add_task(import_stock_prices, body.period)
    return ApiResponse(data=ImportAcceptedResponse(message="stock import started"))


@router.post(
    "/fx-rates",
    summary="Fetch FX buy rates from Sinopac",
    description=(
        "Kicks off a background task that pulls today's (or last-day-of-period) "
        "FX rates from Sinopac and upserts into FX_Rate."
    ),
    response_model=ApiResponse[ImportAcceptedResponse],
    responses=_ACCEPTED_RESPONSES,
    status_code=202,
)
def trigger_fx_import(
    body: ImportRequest, tasks: BackgroundTasks
) -> ApiResponse[ImportAcceptedResponse]:
    tasks.add_task(import_fx_rates, body.period)
    return ApiResponse(data=ImportAcceptedResponse(message="fx import started"))


@router.post(
    "/invoices",
    summary="Import an uploaded government invoice CSV",
    description=(
        "Parses an uploaded pipe-delimited invoice CSV and inserts deduplicated "
        "journal rows. Runs synchronously and returns the import counts."
    ),
    response_model=ApiResponse[InvoiceImportResult],
    responses=_ACCEPTED_RESPONSES,
)
def trigger_invoice_import(
    file: UploadFile = File(..., description="Pipe-delimited invoice CSV"),
) -> ApiResponse[InvoiceImportResult]:
    raw = file.file.read()
    # utf-8-sig strips the BOM the government export tends to prepend; replace
    # keeps a stray byte from aborting the whole import.
    content = raw.decode("utf-8-sig", errors="replace")
    result = import_invoices(content)
    return ApiResponse(data=result)
