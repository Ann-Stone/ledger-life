"""Utilities domain router — selections, health, imports, exports."""
from fastapi import APIRouter

from app.routers.utilities.imports import router as imports_router
from app.routers.utilities.selections import router as selections_router

router = APIRouter(prefix="/utilities", tags=["utilities"])
router.include_router(selections_router)
router.include_router(imports_router)
