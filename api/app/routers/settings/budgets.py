"""Budget management endpoints (Settings domain)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.models.settings.budget import BudgetCreate, BudgetRead, BudgetUpdate
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    error_response,
    not_found_error,
)
from app.services.setting_service import (
    apply_budget,
    bulk_update_budgets,
    list_budget_year_range,
    list_budgets_by_year,
    suggest_budget,
)

router = APIRouter(prefix="/budgets", tags=["settings:budgets"])


@router.get(
    "/year-range",
    summary="Available budget years",
    description="Return distinct budget_year values present in Budget, ascending.",
    response_model=ApiResponse[list[int]],
    responses={422: VALIDATION_ERROR, 500: INTERNAL_ERROR},
)
def list_budget_year_range_endpoint(
    session: Session = Depends(get_session),
) -> ApiResponse[list[int]]:
    return ApiResponse(data=list_budget_year_range(session))


@router.get(
    "/{year}",
    summary="Budgets for a year",
    description="Return all Budget rows for the given year ordered by category_code.",
    response_model=ApiResponse[list[BudgetRead]],
    responses={
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def list_budgets_by_year_endpoint(
    year: int,
    session: Session = Depends(get_session),
) -> ApiResponse[list[BudgetRead]]:
    rows = list_budgets_by_year(session, year)
    return ApiResponse(data=[BudgetRead.model_validate(r, from_attributes=True) for r in rows])


@router.put(
    "",
    summary="Bulk update budgets",
    description=(
        "Update multiple Budget rows in one call. Each item is matched by "
        "(budget_year, category_code). Transactional — if any row is missing, "
        "all updates are rolled back."
    ),
    response_model=ApiResponse[list[BudgetRead]],
    responses={
        404: not_found_error("Budget rows"),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def bulk_update_budgets_endpoint(
    payload: list[BudgetUpdate],
    session: Session = Depends(get_session),
) -> ApiResponse[list[BudgetRead]]:
    rows = bulk_update_budgets(session, payload)
    return ApiResponse(data=[BudgetRead.model_validate(r, from_attributes=True) for r in rows])


@router.post(
    "/{year}/suggest",
    summary="Suggest budget from recent years",
    description=(
        "Compute a suggested budget for {year} from the last up-to-3 years of "
        "Journal spending: per-calendar-month median for ordinary Fixed/Floating "
        "categories, and a single annual-total median envelope (annual_amount) for "
        "categories flagged is_annual_event. Returns the suggestion WITHOUT "
        "persisting so the client can preview and edit before applying."
    ),
    response_model=ApiResponse[list[BudgetRead]],
    responses={
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def suggest_budget_endpoint(
    year: int,
    session: Session = Depends(get_session),
) -> ApiResponse[list[BudgetRead]]:
    rows = suggest_budget(session, year)
    return ApiResponse(data=[BudgetRead.model_validate(r, from_attributes=True) for r in rows])


@router.post(
    "/{year}/apply",
    summary="Apply (upsert) budget rows",
    description=(
        "Upsert the provided budget rows, inserting rows that do not exist yet. "
        "Use this to persist a (possibly edited) suggestion for a brand-new year."
    ),
    response_model=ApiResponse[list[BudgetRead]],
    responses={
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def apply_budget_endpoint(
    year: int,
    payload: list[BudgetCreate],
    session: Session = Depends(get_session),
) -> ApiResponse[list[BudgetRead]]:
    rows = apply_budget(session, payload)
    return ApiResponse(data=[BudgetRead.model_validate(r, from_attributes=True) for r in rows])
