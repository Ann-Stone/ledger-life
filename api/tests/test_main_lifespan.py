"""Lifespan wiring: the startup catch-up is scheduled only when the flag is on.

Each test drives ``main.lifespan`` directly under its own ``asyncio.run`` loop —
no ``TestClient`` portal/thread is shared between tests, so a background task
scheduled by one test cannot leak onto another. The flag is patched on
``main.settings`` (the exact object the lifespan reads), and ``startup_catch_up``
is stubbed to a recording no-op so no real FX/stock network call can fire.
"""
from __future__ import annotations

import asyncio

import pytest
from fastapi import FastAPI

from app import main as main_mod


def _fresh_app() -> FastAPI:
    return FastAPI(lifespan=main_mod.lifespan)


def test_lifespan_schedules_catch_up_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[int] = []
    # Override the autouse test guard; patch the object the lifespan reads.
    monkeypatch.setattr(main_mod.settings, "enable_startup_catch_up", True)
    monkeypatch.setattr(main_mod, "startup_catch_up", lambda: calls.append(1))

    async def _run() -> object:
        app = _fresh_app()
        async with main_mod.lifespan(app):
            pass
        task = getattr(app.state, "catch_up_task", None)
        if task is not None:
            await task  # let the background no-op finish cleanly
        return task

    task = asyncio.run(_run())
    assert task is not None
    assert calls == [1]


def test_lifespan_skips_catch_up_when_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[int] = []
    monkeypatch.setattr(main_mod.settings, "enable_startup_catch_up", False)
    monkeypatch.setattr(main_mod, "startup_catch_up", lambda: calls.append(1))

    async def _run() -> object:
        app = _fresh_app()
        async with main_mod.lifespan(app):
            pass
        return getattr(app.state, "catch_up_task", None)

    task = asyncio.run(_run())
    assert task is None
    assert calls == []
