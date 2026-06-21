"""Telegram transport adapter — the one place that talks to the Telegram API.

Per the integration-contract skill, platform specifics live behind this adapter
so call sites stay platform-free. It owns the mandatory outbound capabilities:

* **chunking** — Telegram caps a message at 4096 chars; longer bodies are split
  in order, never truncated silently.
* **retry** with backoff on transient failures.
* **crash-safety** — a send failure must never propagate to the caller; it is
  logged and swallowed (mirrors ``import_service``'s graceful-degradation posture).

The adapter is intentionally PTB-agnostic: it only needs an object exposing an
async ``send_message(chat_id, text, reply_markup=None)`` (python-telegram-bot's
``Bot`` satisfies this), so it can be unit-tested with a tiny fake.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Protocol

logger = logging.getLogger(__name__)

# Telegram's hard limit for a single text message.
TELEGRAM_MAX_MESSAGE = 4096


class _BotLike(Protocol):
    async def send_message(
        self, chat_id: int, text: str, **kwargs: Any
    ) -> Any: ...  # pragma: no cover - structural type only


def chunk_message(text: str, limit: int = TELEGRAM_MAX_MESSAGE) -> list[str]:
    """Split ``text`` into ordered pieces no longer than ``limit`` characters.

    Splits on newline boundaries when possible so a chunk does not cut through a
    line; falls back to a hard slice for a single over-long line. Never drops or
    truncates content. An empty string yields a single empty chunk so the caller
    still sends one message.
    """
    if limit <= 0:
        raise ValueError("limit must be positive")
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    current = ""
    for line in text.split("\n"):
        # A single line longer than the limit is hard-sliced into limit-sized pieces.
        while len(line) > limit:
            if current:
                chunks.append(current)
                current = ""
            chunks.append(line[:limit])
            line = line[limit:]
        candidate = line if not current else f"{current}\n{line}"
        if len(candidate) > limit:
            chunks.append(current)
            current = line
        else:
            current = candidate
    chunks.append(current)
    return chunks


class TelegramTransport:
    """Wraps a Telegram ``Bot`` with chunking, retry, and crash-safe sends."""

    def __init__(
        self, bot: _BotLike, *, max_retries: int = 2, backoff_base: float = 0.5
    ) -> None:
        self._bot = bot
        self._max_retries = max_retries
        self._backoff_base = backoff_base

    async def send(
        self, chat_id: int, text: str, *, reply_markup: Any | None = None
    ) -> bool:
        """Send ``text`` to ``chat_id``; return True on success, False otherwise.

        Long messages are chunked; only the first chunk carries ``reply_markup``
        (the inline keyboard). Any exception is retried with backoff and finally
        logged and swallowed — the caller is never crashed by a transport error.
        """
        ok = True
        for index, chunk in enumerate(chunk_message(text)):
            markup = reply_markup if index == 0 else None
            ok = await self._send_one(chat_id, chunk, markup) and ok
        return ok

    async def _send_one(
        self, chat_id: int, text: str, reply_markup: Any | None
    ) -> bool:
        attempt = 0
        while True:
            try:
                await self._bot.send_message(
                    chat_id=chat_id, text=text, reply_markup=reply_markup
                )
                return True
            except Exception as exc:  # noqa: BLE001 - adapter must never crash caller
                attempt += 1
                if attempt > self._max_retries:
                    logger.warning(
                        "Telegram send to %s failed after %d attempts: %s",
                        chat_id,
                        attempt,
                        exc,
                    )
                    return False
                # Honour Telegram's RetryAfter hint when present, else backoff.
                delay = getattr(exc, "retry_after", None)
                if not isinstance(delay, (int, float)):
                    delay = self._backoff_base * (2 ** (attempt - 1))
                await asyncio.sleep(delay)
