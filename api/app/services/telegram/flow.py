"""python-telegram-bot handlers for the guided record flow.

Conversation: a free-text ``amount [note]`` message starts a draft, then three
inline-keyboard taps fill it — 支出/收入 → 分類 → 帳戶/卡片 → ✅ 確認 — and the entry is
written via :func:`record_draft`. Interactive keyboard transitions edit the card
in place (``edit_message_text``); fresh top-level messages (prompt / help /
refusal / cancel) go through :func:`notify`, the single outbound entry point.

Per-conversation state lives in ``context.user_data`` (PTB keeps it per chat);
the shared transport lives in ``context.bot_data['transport']``.
"""
from __future__ import annotations

import logging

from sqlmodel import Session
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.database import engine
from app.services.telegram.dispatch import is_allowed
from app.services.telegram.notify import notify
from app.services.telegram.recording import (
    EXPENSE,
    INCOME,
    JournalDraft,
    category_options,
    parse_amount_note,
    payment_options,
    record_draft,
    signed_spending,
)
from app.services.telegram.transport import TelegramTransport

logger = logging.getLogger(__name__)

_DIRECTION_LABEL = {EXPENSE: "支出", INCOME: "收入"}

USAGE = (
    "👋 記帳機器人\n"
    "直接輸入「金額 [備註]」開始，例如：\n"
    "  120 午餐\n"
    "  500 加油\n"
    "接著依序點選 支出/收入 → 分類 → 帳戶 即可。\n"
    "/cancel 取消目前這筆。"
)
_STALE = "這筆已結束或逾時，請重新輸入金額，例如：120 午餐"


def _transport(context: ContextTypes.DEFAULT_TYPE) -> TelegramTransport:
    return context.bot_data["transport"]


def _fmt_amount(value: float) -> str:
    return f"{int(value):,}" if value == int(value) else f"{value:,.2f}"


def _grid(buttons: list[InlineKeyboardButton], per_row: int = 2) -> InlineKeyboardMarkup:
    rows = [buttons[i : i + per_row] for i in range(0, len(buttons), per_row)]
    return InlineKeyboardMarkup(rows)


def _clear(context: ContextTypes.DEFAULT_TYPE) -> None:
    for key in ("draft", "cat_types", "cat_labels", "pay_types", "pay_labels"):
        context.user_data.pop(key, None)


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    transport = _transport(context)
    parsed = parse_amount_note(update.message.text or "")
    if parsed is None:
        await notify(transport, chat_id, "info", USAGE)
        return
    amount, note = parsed
    context.user_data.clear()
    context.user_data["draft"] = JournalDraft(amount=amount, note=note)
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🟥 支出", callback_data=f"dir:{EXPENSE}"),
                InlineKeyboardButton("🟩 收入", callback_data=f"dir:{INCOME}"),
            ]
        ]
    )
    note_str = f"（{note}）" if note else ""
    await notify(
        transport,
        chat_id,
        "info",
        f"金額 {_fmt_amount(amount)}{note_str}\n請選擇方向：",
        reply_markup=keyboard,
    )


async def on_direction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not is_allowed(update.effective_chat.id):
        return
    draft: JournalDraft | None = context.user_data.get("draft")
    if draft is None:
        await query.edit_message_text(_STALE)
        return
    direction = query.data.split(":", 1)[1]
    draft.direction = direction
    with Session(engine) as session:
        options = category_options(session, direction)
    if not options:
        await query.edit_message_text(
            f"尚未設定任何「{_DIRECTION_LABEL.get(direction, direction)}」分類，請先到設定建立。"
        )
        return
    context.user_data["cat_types"] = {o.code_id: o.code_type for o in options}
    context.user_data["cat_labels"] = {o.code_id: o.label for o in options}
    buttons = [
        InlineKeyboardButton(o.label, callback_data=f"cat:{o.code_id}") for o in options
    ]
    await query.edit_message_text(
        f"方向：{_DIRECTION_LABEL.get(direction, direction)}\n請選擇分類：",
        reply_markup=_grid(buttons),
    )


async def on_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not is_allowed(update.effective_chat.id):
        return
    draft: JournalDraft | None = context.user_data.get("draft")
    if draft is None or draft.direction is None:
        await query.edit_message_text(_STALE)
        return
    code_id = query.data.split(":", 1)[1]
    draft.action_main = code_id
    draft.action_main_type = context.user_data.get("cat_types", {}).get(code_id)
    with Session(engine) as session:
        pays = payment_options(session)
    if not pays:
        await query.edit_message_text("尚未設定任何帳戶或信用卡，請先到設定建立。")
        return
    context.user_data["pay_types"] = {p.value: p.spend_way_type for p in pays}
    context.user_data["pay_labels"] = {p.value: p.label for p in pays}
    buttons = [
        InlineKeyboardButton(p.label, callback_data=f"pay:{p.value}") for p in pays
    ]
    await query.edit_message_text("請選擇支付來源：", reply_markup=_grid(buttons))


async def on_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not is_allowed(update.effective_chat.id):
        return
    draft: JournalDraft | None = context.user_data.get("draft")
    if draft is None or draft.action_main is None:
        await query.edit_message_text(_STALE)
        return
    value = query.data.split(":", 1)[1]
    draft.spend_way = value
    draft.spend_way_type = context.user_data.get("pay_types", {}).get(value)

    cat_label = context.user_data.get("cat_labels", {}).get(draft.action_main, draft.action_main)
    pay_label = context.user_data.get("pay_labels", {}).get(value, value)
    summary = (
        "請確認：\n"
        f"  方向：{_DIRECTION_LABEL.get(draft.direction, draft.direction)}\n"
        f"  金額：{_fmt_amount(draft.amount)}\n"
        f"  分類：{cat_label}\n"
        f"  來源：{pay_label}"
    )
    if draft.note:
        summary += f"\n  備註：{draft.note}"
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ 確認", callback_data="ok"),
                InlineKeyboardButton("❌ 取消", callback_data="cancel"),
            ]
        ]
    )
    await query.edit_message_text(summary, reply_markup=keyboard)


async def on_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if not is_allowed(update.effective_chat.id):
        return
    draft: JournalDraft | None = context.user_data.get("draft")
    if draft is None:
        await query.edit_message_text(_STALE)
        return
    try:
        with Session(engine) as session:
            row = record_draft(session, draft)
        signed = signed_spending(draft.amount, draft.direction)
        sign = "+" if signed >= 0 else "-"
        note_str = f" {draft.note}" if draft.note else ""
        await query.edit_message_text(
            f"✅ 已記錄 #{row.distinct_number}：{sign}{_fmt_amount(abs(signed))}{note_str}"
        )
    except Exception as exc:  # noqa: BLE001 - report failure, never crash the poller
        logger.exception("Failed to record journal from Telegram")
        await query.edit_message_text(f"🛑 記錄失敗：{exc}")
    finally:
        _clear(context)


async def on_cancel_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    _clear(context)
    await query.edit_message_text("已取消。")


async def on_cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _clear(context)
    await notify(_transport(context), update.effective_chat.id, "info", "已取消。")


async def on_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await notify(_transport(context), update.effective_chat.id, "info", USAGE)


async def on_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await notify(
        _transport(context), update.effective_chat.id, "info", f"未知指令。\n{USAGE}"
    )


def register_handlers(application: Application, allowed_chat_id: int) -> None:
    """Register all handlers, gated by ``filters.Chat`` (the allow-list)."""
    chat_filter = filters.Chat(allowed_chat_id)
    # Known commands first, generic unknown-command handler last.
    application.add_handler(CommandHandler("start", on_start, filters=chat_filter))
    application.add_handler(CommandHandler("help", on_start, filters=chat_filter))
    application.add_handler(CommandHandler("cancel", on_cancel_cmd, filters=chat_filter))
    application.add_handler(CallbackQueryHandler(on_direction, pattern=r"^dir:"))
    application.add_handler(CallbackQueryHandler(on_category, pattern=r"^cat:"))
    application.add_handler(CallbackQueryHandler(on_payment, pattern=r"^pay:"))
    application.add_handler(CallbackQueryHandler(on_confirm, pattern=r"^ok$"))
    application.add_handler(CallbackQueryHandler(on_cancel_cb, pattern=r"^cancel$"))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND & chat_filter, on_text)
    )
    application.add_handler(
        MessageHandler(filters.COMMAND & chat_filter, on_unknown)
    )
