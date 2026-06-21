"""Inbound dispatch guards: the permission hook and namespace convention.

Per the integration-contract skill, a permission/authz hook is checked before a
command is dispatched. Here that hook is the **chat-id allow-list** — the bot
token is publicly reachable, so only the owner's chat may be served. This is the
first-class authz check, not an ad-hoc ``if`` scattered in handlers.

python-telegram-bot *is* the dispatcher (its CommandHandler / CallbackQueryHandler
registry routes updates), so we don't build a parallel engine over it. We add two
things on top: ``is_allowed`` (the hook, also applied as a ``filters.Chat`` at
registration for defence-in-depth) and the command **namespace** convention.

Namespace: phase-2 commands are named ``networth.<verb>`` (surfaced as
``/<verb>`` on a single-service bot). If this bot's token is ever shared with
another service, prefixing keeps ``/balance`` etc. from colliding across services
that all arrive through the one poller (see the schedule-task one-poller rule).
"""
from __future__ import annotations

from app.config import settings

COMMAND_NAMESPACE = "networth"


def is_allowed(chat_id: int | None) -> bool:
    """True only for the allow-listed owner chat (the dispatch permission hook).

    Returns False when no allow-list is configured (chat id 0) so a misconfigured
    bot serves nobody rather than everybody.
    """
    allowed = settings.telegram_allowed_chat_id
    return bool(allowed) and chat_id == allowed
