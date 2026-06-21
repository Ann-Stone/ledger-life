"""Cash-flow statement (現金流量表) endpoint — 生活 / 投資 / 債務 activities."""
from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database import get_session
from app.models.reports.cash_flow import CashFlowRead
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
)
from app.services.report_service import get_cash_flow

router = APIRouter()


@router.get(
    "/cash-flow/{type}",
    summary="Get personal cash-flow statement",
    description=(
        "Cash flow over the monthly (trailing 12 months) or yearly (trailing 10 "
        "years) window, split into three activities: operating (生活: income − "
        "living − loan interest), investing (投資), financing (債務: loan "
        "principal / new borrowing). FX-converted; self-transfers excluded."
    ),
    response_model=ApiResponse[CashFlowRead],
    responses={
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def get_cash_flow_endpoint(
    type: Literal["monthly", "yearly"],
    vesting_month: Annotated[
        str,
        Query(
            ...,
            description="Anchor month YYYYMM",
            examples=["202412"],
            pattern=r"^\d{6}$",
        ),
    ],
    session: Session = Depends(get_session),
) -> ApiResponse[CashFlowRead]:
    return ApiResponse(data=get_cash_flow(session, type, vesting_month))
