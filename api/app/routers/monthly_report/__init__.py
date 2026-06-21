from fastapi import APIRouter

from app.routers.monthly_report.balance import router as balance_router
from app.routers.monthly_report.estate_values import router as estate_values_router
from app.routers.monthly_report.insurance_values import router as insurance_values_router
from app.routers.monthly_report.journals import router as journals_router
from app.routers.monthly_report.stock_prices import router as stock_prices_router

router = APIRouter(prefix="/monthly-report", tags=["monthly_report"])
router.include_router(journals_router, prefix="/journals", tags=["monthly-report"])
router.include_router(stock_prices_router, prefix="/stock-prices", tags=["monthly-report"])
router.include_router(
    insurance_values_router, prefix="/insurance-values", tags=["monthly-report"]
)
router.include_router(
    estate_values_router, prefix="/estate-values", tags=["monthly-report"]
)
router.include_router(balance_router, prefix="/balance", tags=["monthly-report"])
