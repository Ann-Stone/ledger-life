"""Process lifecycle for the embedded bot — build it, and start/stop it inside
the API's existing asyncio loop (driven from ``main.lifespan``).

We deliberately use ``initialize/start/updater.start_polling`` rather than
``Application.run_polling()``: the latter creates and owns its own event loop,
which would conflict with the uvicorn loop the API already runs on.
"""
from __future__ import annotations

import logging

from telegram.ext import Application

from app.config import settings
from app.services.telegram.flow import register_handlers
from app.services.telegram.transport import TelegramTransport

logger = logging.getLogger(__name__)


def build_application() -> Application:
    """Build the PTB Application, wire the transport and handlers."""
    token = settings.telegram_bot_token
    if not token:
        raise RuntimeError("telegram_bot_token is not set")
    application = Application.builder().token(token).build()
    application.bot_data["transport"] = TelegramTransport(application.bot)
    register_handlers(application, settings.telegram_allowed_chat_id)
    return application


async def start_bot(application: Application) -> None:
    """Initialize and start long-polling within the current event loop."""
    await application.initialize()
    await application.start()
    # drop_pending_updates: don't replay a backlog accrued while the PC was off.
    await application.updater.start_polling(drop_pending_updates=True)
    logger.info("Telegram bot started (long polling)")


async def stop_bot(application: Application) -> None:
    """Stop polling and shut the Application down cleanly (best-effort)."""
    updater = application.updater
    if updater is not None and updater.running:
        await updater.stop()
    if application.running:
        await application.stop()
    await application.shutdown()
    logger.info("Telegram bot stopped")
