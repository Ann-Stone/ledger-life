from fastapi import APIRouter

from app.routers.assets.estates import router as estates_router
from app.routers.assets.insurances import router as insurances_router
from app.routers.assets.loans import router as loans_router
from app.routers.assets.other_assets import router as other_assets_router
from app.routers.assets.stocks import router as stocks_router

router = APIRouter(prefix="/assets", tags=["assets"])
router.include_router(stocks_router, prefix="/stocks", tags=["assets:stocks"])
router.include_router(insurances_router, prefix="/insurances", tags=["assets:insurances"])
router.include_router(estates_router, prefix="/estates", tags=["assets:estates"])
router.include_router(loans_router, prefix="/loans", tags=["assets:loans"])
router.include_router(other_assets_router, prefix="/other-assets", tags=["assets:other-assets"])
