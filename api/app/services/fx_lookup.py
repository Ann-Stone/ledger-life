"""Shared FX-rate lookup with an explicit missing-rate policy.

Window selection is identical for every caller: largest ``import_date <=
YYYYMM31`` for the currency, falling back to the latest prior row of any
date. What differs — and is load-bearing — is what happens when no row
exists at all:

- ``on_missing="raise"`` (settlement): raise ``ValueError`` so the whole
  settlement rolls back instead of snapshotting with a fabricated rate.
- ``on_missing="fallback"`` (reports / monthly views): return ``1.0`` so
  read-only views degrade gracefully. A falsy currency also short-circuits
  to 1.0 under this policy only.
"""
from __future__ import annotations

from typing import Literal

from sqlmodel import Session, select

from app.models.dashboard.fx_rate import FXRate
from app.services.month_utils import month_end

BASE_CURRENCY = "TWD"


def fx_rate_for_month(
    session: Session,
    currency: str | None,
    yyyymm: str,
    *,
    on_missing: Literal["raise", "fallback"] = "fallback",
) -> float:
    """Return ``FXRate.buy_rate`` effective for ``yyyymm`` (see module doc)."""
    if currency == BASE_CURRENCY or (not currency and on_missing == "fallback"):
        return 1.0
    in_window = (
        select(FXRate)
        .where(FXRate.code == currency)
        .where(FXRate.import_date <= month_end(yyyymm))
        .order_by(FXRate.import_date.desc())
    )
    row = session.exec(in_window).first()
    if row is not None:
        return row.buy_rate
    fallback = (
        select(FXRate).where(FXRate.code == currency).order_by(FXRate.import_date.desc())
    )
    row = session.exec(fallback).first()
    if row is not None:
        return row.buy_rate
    if on_missing == "raise":
        raise ValueError(f"No FXRate available for currency {currency}")
    return 1.0
