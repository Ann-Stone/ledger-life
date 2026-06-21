"""Unit tests for the embedded Telegram bookkeeping bot.

Covers the parts that carry the logic, without standing up a real bot:
  * transport — chunking + crash-safe sends (driven via ``asyncio.run`` since the
    project has no pytest-asyncio plugin; mirrors test_main_lifespan.py).
  * dispatch — the chat-id permission hook.
  * recording — parsing, the sign convention, category/payment option derivation,
    and that a complete draft persists the right Journal via ``create_journal``.
  * main.lifespan — the bot is started only when enabled (build/start stubbed).
"""
from __future__ import annotations

import asyncio
from datetime import date

import pytest
from fastapi import FastAPI
from sqlmodel import Session

from app.models.settings.account import Account
from app.models.settings.code_data import CodeData
from app.models.settings.credit_card import CreditCard
from app.services.telegram import dispatch
from app.services.telegram.recording import (
    JournalDraft,
    category_options,
    draft_to_journal_create,
    parse_amount_note,
    payment_options,
    record_draft,
    signed_spending,
)
from app.services.telegram.transport import (
    TELEGRAM_MAX_MESSAGE,
    TelegramTransport,
    chunk_message,
)


# --------------------------------------------------------------------------- #
# transport
# --------------------------------------------------------------------------- #
class _FakeBot:
    def __init__(self, *, fail: bool = False) -> None:
        self.calls: list[dict] = []
        self._fail = fail

    async def send_message(self, chat_id, text, reply_markup=None):
        if self._fail:
            raise RuntimeError("boom")
        self.calls.append(
            {"chat_id": chat_id, "text": text, "reply_markup": reply_markup}
        )


def test_chunk_short_returns_single():
    assert chunk_message("hello") == ["hello"]


def test_chunk_long_single_line_preserves_content():
    text = "a" * (TELEGRAM_MAX_MESSAGE * 2 + 100)
    chunks = chunk_message(text)
    assert len(chunks) >= 3
    assert all(len(c) <= TELEGRAM_MAX_MESSAGE for c in chunks)
    assert "".join(chunks) == text


def test_chunk_multiline_stays_within_limit_and_reconstructs():
    text = "\n".join(f"line-{i}" for i in range(60))
    chunks = chunk_message(text, limit=20)
    assert all(len(c) <= 20 for c in chunks)
    assert "\n".join(chunks) == text


def test_send_success_passes_reply_markup():
    bot = _FakeBot()
    transport = TelegramTransport(bot, max_retries=0)
    ok = asyncio.run(transport.send(123, "hi", reply_markup="KB"))
    assert ok is True
    assert len(bot.calls) == 1
    assert bot.calls[0]["chat_id"] == 123
    assert bot.calls[0]["reply_markup"] == "KB"


def test_send_chunks_and_marks_only_first():
    bot = _FakeBot()
    transport = TelegramTransport(bot, max_retries=0)
    ok = asyncio.run(transport.send(1, "a" * (TELEGRAM_MAX_MESSAGE * 2 + 5), reply_markup="KB"))
    assert ok is True
    assert len(bot.calls) >= 3
    assert bot.calls[0]["reply_markup"] == "KB"
    assert all(c["reply_markup"] is None for c in bot.calls[1:])


def test_send_swallows_failure_without_raising():
    bot = _FakeBot(fail=True)
    transport = TelegramTransport(bot, max_retries=0)
    ok = asyncio.run(transport.send(1, "hi"))
    assert ok is False  # logged + swallowed, did not raise


# --------------------------------------------------------------------------- #
# dispatch (permission hook)
# --------------------------------------------------------------------------- #
def test_is_allowed_only_owner(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(dispatch.settings, "telegram_allowed_chat_id", 555)
    assert dispatch.is_allowed(555) is True
    assert dispatch.is_allowed(999) is False
    assert dispatch.is_allowed(None) is False


def test_is_allowed_unconfigured_serves_nobody(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(dispatch.settings, "telegram_allowed_chat_id", 0)
    assert dispatch.is_allowed(0) is False
    assert dispatch.is_allowed(123) is False


# --------------------------------------------------------------------------- #
# recording — parsing + sign convention
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "text,expected",
    [
        ("120 午餐", (120.0, "午餐")),
        ("午餐 120", (120.0, "午餐")),
        ("3,500 房租", (3500.0, "房租")),
        ("120", (120.0, None)),
        ("12.5 coffee", (12.5, "coffee")),
        ("-300 退款", (300.0, "退款")),
    ],
)
def test_parse_amount_note(text, expected):
    assert parse_amount_note(text) == expected


@pytest.mark.parametrize("text", ["hello", "", "0", "0 nothing"])
def test_parse_amount_note_rejects(text):
    assert parse_amount_note(text) is None


def test_signed_spending_convention():
    assert signed_spending(100, "expense") == -100
    assert signed_spending(100, "income") == 100
    # Anything that isn't income defaults to expense (negative).
    assert signed_spending(100, "whatever") == -100


# --------------------------------------------------------------------------- #
# recording — option derivation from the live selection groups
# --------------------------------------------------------------------------- #
def _seed_codes(session: Session) -> None:
    rows = [
        CodeData(code_id="FLO01", code_type="Floating", name="Food", in_use="Y", code_index=1),
        CodeData(code_id="FIX01", code_type="Fixed", name="Rent", in_use="Y", code_index=2),
        CodeData(code_id="INC01", code_type="Income", name="Salary", in_use="Y", code_index=3),
        CodeData(code_id="PAS01", code_type="Passive", name="Dividend", in_use="Y", code_index=4),
        CodeData(code_id="INV01", code_type="Invest", name="Stock", in_use="Y", code_index=5),
        # A sub-code (has parent_id) must never appear as a top-level option.
        CodeData(code_id="SUB01", code_type="Floating", name="Snack", parent_id="FLO01", in_use="Y", code_index=6),
        # Inactive top-level code must be excluded.
        CodeData(code_id="FLO99", code_type="Floating", name="Old", in_use="N", code_index=7),
    ]
    for r in rows:
        session.add(r)
    session.commit()


def test_category_options_expense(session: Session):
    _seed_codes(session)
    opts = category_options(session, "expense")
    assert {o.code_id for o in opts} == {"FLO01", "FIX01"}
    # group label flows through as action_main_type
    assert {o.code_type for o in opts} == {"Floating", "Fixed"}


def test_category_options_income_includes_passive(session: Session):
    _seed_codes(session)
    assert {o.code_id for o in category_options(session, "income")} == {"INC01", "PAS01"}


def test_payment_options_tags_types(session: Session):
    session.add(
        Account(
            account_id="ACC-1", name="玉山", account_type="bank", fx_code="TWD",
            is_calculate="Y", in_use="Y", discount=1.0, account_index=1,
        )
    )
    session.add(
        CreditCard(
            credit_card_id="CC-1", card_name="VISA", fx_code="TWD",
            in_use="Y", credit_card_index=1,
        )
    )
    session.commit()
    opts = payment_options(session)
    assert {o.spend_way_type for o in opts} == {"account", "credit_card"}
    acc = next(o for o in opts if o.spend_way_type == "account")
    assert acc.value == "1"  # Account PK, stringified
    cc = next(o for o in opts if o.spend_way_type == "credit_card")
    assert cc.value == "CC-1"


# --------------------------------------------------------------------------- #
# recording — a complete draft persists the right Journal
# --------------------------------------------------------------------------- #
def test_record_draft_expense_via_account(session: Session):
    draft = JournalDraft(
        amount=120.0, note="午餐", direction="expense",
        action_main="FLO01", action_main_type="Floating",
        spend_way="1", spend_way_type="account",
    )
    row = record_draft(session, draft, today=date(2026, 6, 20))
    assert row.distinct_number is not None
    assert row.spending == -120.0  # expense → negative
    assert row.action_main == "FLO01"
    assert row.action_main_type == "Floating"
    assert row.action_main_table == "Code_Data"
    assert row.spend_way == "1"
    assert row.spend_way_type == "account"
    assert row.spend_way_table == "Account"
    assert row.vesting_month == "202606"
    assert row.spend_date == "20260620"
    assert row.note == "午餐"
    assert row.action_sub is None


def test_record_draft_income_via_credit_card(session: Session):
    draft = JournalDraft(
        amount=5000.0, direction="income",
        action_main="INC01", action_main_type="Income",
        spend_way="CC-1", spend_way_type="credit_card",
    )
    row = record_draft(session, draft, today=date(2026, 6, 20))
    assert row.spending == 5000.0  # income → positive
    assert row.spend_way_table == "Credit_Card"


def test_incomplete_draft_raises():
    draft = JournalDraft(amount=10.0, direction="expense")  # no category / payment
    with pytest.raises(ValueError):
        draft_to_journal_create(draft, today=date(2026, 6, 20))


# --------------------------------------------------------------------------- #
# main.lifespan wiring (bot start/stop, build/start stubbed)
# --------------------------------------------------------------------------- #
def test_lifespan_starts_and_stops_bot_when_enabled(monkeypatch: pytest.MonkeyPatch):
    from app import main as main_mod
    import app.services.telegram.bot as bot_mod

    monkeypatch.setattr(main_mod.settings, "enable_startup_catch_up", False)
    monkeypatch.setattr(main_mod.settings, "telegram_bot_enabled", True)
    monkeypatch.setattr(main_mod.settings, "telegram_bot_token", "TESTTOKEN")

    fake_app = object()
    events: dict[str, object] = {}
    monkeypatch.setattr(bot_mod, "build_application", lambda: fake_app)

    async def _start(app):
        events["start"] = app

    async def _stop(app):
        events["stop"] = app

    monkeypatch.setattr(bot_mod, "start_bot", _start)
    monkeypatch.setattr(bot_mod, "stop_bot", _stop)

    async def _run():
        app = FastAPI(lifespan=main_mod.lifespan)
        async with main_mod.lifespan(app):
            state = getattr(app.state, "telegram_app", None)
        return state

    result = asyncio.run(_run())
    assert result is fake_app
    assert events.get("start") is fake_app
    assert events.get("stop") is fake_app


def test_lifespan_skips_bot_when_disabled(monkeypatch: pytest.MonkeyPatch):
    from app import main as main_mod

    monkeypatch.setattr(main_mod.settings, "enable_startup_catch_up", False)
    monkeypatch.setattr(main_mod.settings, "telegram_bot_enabled", False)

    async def _run():
        app = FastAPI(lifespan=main_mod.lifespan)
        async with main_mod.lifespan(app):
            pass
        return getattr(app.state, "telegram_app", None)

    assert asyncio.run(_run()) is None
