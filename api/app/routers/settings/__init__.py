from fastapi import APIRouter

from app.routers.settings.accounts import router as accounts_router
from app.routers.settings.alarms import router as alarms_router
from app.routers.settings.budgets import router as budgets_router
from app.routers.settings.codes import router as codes_router
from app.routers.settings.credit_cards import router as credit_cards_router
from app.routers.settings.stock_categories import router as stock_categories_router
from app.routers.settings.sub_codes import router as sub_codes_router

router = APIRouter(prefix="/settings", tags=["settings"])
router.include_router(accounts_router)
router.include_router(alarms_router)
router.include_router(budgets_router)
router.include_router(codes_router)
router.include_router(credit_cards_router)
router.include_router(stock_categories_router)
router.include_router(sub_codes_router)
