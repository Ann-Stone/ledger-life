"""Telegram bookkeeping bot — embedded in the API, started from the lifespan.

The bot lets the owner log an income/expense entry from Telegram in a few taps
and writes it straight into the ledger via ``create_journal`` — no settlement
step, immediately visible.

Structure follows the integration-contract skill: Telegram specifics live behind
a transport **adapter** (`transport.py`); all outbound messages go through one
``notify`` entry point (`notify.py`); inbound updates pass a **permission hook**
before dispatch (`dispatch.py`); the domain logic that turns a guided-button
draft into a journal is pure and testable (`recording.py`); the PTB wiring lives
in `flow.py`, and the process lifecycle in `bot.py`.
"""
