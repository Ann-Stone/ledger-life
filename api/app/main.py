import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import create_db_and_tables
from app.services.import_service import startup_catch_up
from app.routers.assets import router as assets_router
from app.routers.dashboard import router as dashboard_router
from app.routers.health import router as health_router
from app.routers.monthly_report import router as monthly_report_router
from app.routers.reports import router as reports_router
from app.routers.settings import router as settings_router
from app.routers.utilities import router as utilities_router
from app.schemas.response import ApiError

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables, fire the month-end backfill, and start the Telegram bot."""
    create_db_and_tables()
    if settings.enable_startup_catch_up:
        # Run off the event loop so slow FX/stock fetches never block startup.
        # Keep a reference so the task is not garbage-collected mid-flight.
        app.state.catch_up_task = asyncio.create_task(
            asyncio.to_thread(startup_catch_up)
        )

    # Embedded Telegram bookkeeping bot (long polling). A failure here must
    # never block the API from coming up, so it is logged and swallowed.
    bot_app = None
    if settings.telegram_bot_enabled and settings.telegram_bot_token:
        try:
            from app.services.telegram.bot import build_application, start_bot

            bot_app = build_application()
            await start_bot(bot_app)
            app.state.telegram_app = bot_app
        except Exception:  # noqa: BLE001 - never block startup on the bot
            logger.exception("Telegram bot failed to start")
            bot_app = None

    yield

    if bot_app is not None:
        from app.services.telegram.bot import stop_bot

        await stop_bot(bot_app)


app = FastAPI(title="Networth API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def on_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiError(error=exc.detail).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def on_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=ApiError(error=exc.errors()).model_dump(),
    )


@app.exception_handler(ValueError)
async def on_value_error(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content=ApiError(error=str(exc)).model_dump(),
    )


@app.exception_handler(Exception)
async def on_exception(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=ApiError(error=str(exc)).model_dump(),
    )


app.include_router(settings_router)
app.include_router(monthly_report_router)
app.include_router(assets_router)
app.include_router(reports_router)
app.include_router(dashboard_router)
app.include_router(utilities_router)
app.include_router(health_router)
