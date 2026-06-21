from fastapi import APIRouter

from app.routers.dashboard.alarms import router as alarms_router
from app.routers.dashboard.budget import router as budget_router
from app.routers.dashboard.gifts import router as gifts_router
from app.routers.dashboard.summary import router as summary_router
from app.routers.dashboard.targets import router as targets_router

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
router.include_router(summary_router)
router.include_router(budget_router)
router.include_router(targets_router)
router.include_router(alarms_router)
router.include_router(gifts_router)
