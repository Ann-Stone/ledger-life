"""The single outbound entry point: ``notify(target, level, message)``.

Per the integration-contract skill, every outbound message routes through here
rather than scattered raw API calls. ``target`` is a logical name resolved to a
chat id (no raw ids at call sites); ``level`` ∈ {info, warning, error} maps to a
prefix. The actual send is delegated to the transport adapter, which owns
chunking/retry/crash-safety.

``alert(...)`` is the error-class specialisation (``notify(level="error",
target="ops")``). Fingerprint dedup/throttle is a phase-2 concern — stubbed here
so error reporting already flows through one shape.
"""
from __future__ import annotations

from typing import Literal

from app.config import settings
from app.services.telegram.transport import TelegramTransport

Level = Literal["info", "warning", "error"]

_LEVEL_PREFIX: dict[Level, str] = {
    "info": "",
    "warning": "⚠️ ",
    "error": "🛑 ",
}


def resolve_target(target: str) -> int:
    """Resolve a logical target name to a Telegram chat id.

    For this solo deployment both ``"user"`` and ``"ops"`` map to the single
    allow-listed owner chat. Keeping the indirection means call sites never carry
    raw chat ids and a future multi-recipient setup only changes this function.
    """
    return settings.telegram_allowed_chat_id


async def notify(
    transport: TelegramTransport,
    target: str | int,
    level: Level,
    message: str,
    *,
    reply_markup: object | None = None,
) -> bool:
    """Send ``message`` at ``level`` to ``target`` (a logical name or a chat id)."""
    chat_id = target if isinstance(target, int) else resolve_target(target)
    text = f"{_LEVEL_PREFIX.get(level, '')}{message}"
    return await transport.send(chat_id, text, reply_markup=reply_markup)


async def alert(transport: TelegramTransport, message: str) -> bool:
    """Error-class alert to the ops target. (Phase-2: add fingerprint dedup.)"""
    return await notify(transport, "ops", "error", message)
