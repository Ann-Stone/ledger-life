"""Estate market-value service — record/query real-estate appraisals over time.

The settlement step consumes :func:`select_month_market_value` to value each
property; the monthly-report endpoints use :func:`list_month_estate_values` and
:func:`upsert_estate_value`. Mirrors ``insurance_value_service``.
"""
from __future__ import annotations

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.assets.estate import Estate
from app.models.assets.estate_value_history import (
    EstateValueCreate,
    EstateValueHistory,
    EstateValueMonthRead,
)


def select_month_market_value(
    session: Session, estate_id: str, vesting_month: str
) -> EstateValueHistory | None:
    """Latest recorded market value for an estate on or before ``vesting_month``.

    Carries a value forward: an appraisal entered in an earlier month applies
    until a newer one is entered. Returns ``None`` when nothing has ever been
    recorded, so callers can fall back to cost.
    """
    stmt = (
        select(EstateValueHistory)
        .where(EstateValueHistory.estate_id == estate_id)
        .where(EstateValueHistory.vesting_month <= vesting_month)
        .order_by(EstateValueHistory.vesting_month.desc())
    )
    return session.exec(stmt).first()


def list_month_estate_values(
    session: Session, vesting_month: str
) -> list[EstateValueMonthRead]:
    """Per-estate market value as of a month (latest recorded, carried forward).

    Every estate is emitted so the UI can show which still need an appraisal:
    ``recorded`` is True only when the value was entered in this exact month.
    """
    estates = list(session.exec(select(Estate)).all())
    out: list[EstateValueMonthRead] = []
    for e in estates:
        row = select_month_market_value(session, e.estate_id, vesting_month)
        out.append(
            EstateValueMonthRead(
                estate_id=e.estate_id,
                estate_name=e.estate_name,
                market_value=row.market_value if row is not None else None,
                vesting_month=row.vesting_month if row is not None else None,
                recorded=bool(row is not None and row.vesting_month == vesting_month),
            )
        )
    return out


def upsert_estate_value(
    session: Session, payload: EstateValueCreate
) -> EstateValueHistory:
    """Insert or update the market value for an (estate, month).

    Idempotent on the composite PK; 404s when the estate does not exist.
    """
    if session.get(Estate, payload.estate_id) is None:
        raise HTTPException(
            status_code=404, detail=f"Estate not found: {payload.estate_id}"
        )
    existing = session.get(
        EstateValueHistory, (payload.estate_id, payload.vesting_month)
    )
    if existing is not None:
        existing.market_value = payload.market_value
        existing.memo = payload.memo
        row = existing
    else:
        row = EstateValueHistory(**payload.model_dump())
    session.add(row)
    session.commit()
    session.refresh(row)
    return row
