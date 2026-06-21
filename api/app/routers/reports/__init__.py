from fastapi import APIRouter

from app.routers.reports.assets import router as assets_router
from app.routers.reports.balance import router as balance_router
from app.routers.reports.budget_variance import router as budget_variance_router
from app.routers.reports.cash_flow import router as cash_flow_router
from app.routers.reports.expenditure import router as expenditure_router
from app.routers.reports.expenditure_composition import (
    router as expenditure_composition_router,
)
from app.routers.reports.expense_insights import router as expense_insights_router
from app.routers.reports.income_expense import router as income_expense_router
from app.routers.reports.income_statement import router as income_statement_router

router = APIRouter(prefix="/reports", tags=["reports"])
router.include_router(balance_router)
router.include_router(budget_variance_router)
router.include_router(cash_flow_router)
router.include_router(expenditure_router)
router.include_router(expenditure_composition_router)
router.include_router(expense_insights_router)
router.include_router(income_expense_router)
router.include_router(income_statement_router)
router.include_router(assets_router)
