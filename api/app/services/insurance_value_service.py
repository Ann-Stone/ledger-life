"""Insurance surrender-value service — record/query policy 解約金 over time.

The settlement step consumes :func:`select_month_surrender_value` to value each
policy; the monthly-report endpoints use :func:`list_month_insurance_values` and
:func:`upsert_insurance_value`. Mirrors ``stock_service`` (close-price selection
+ insert) so the surrender value behaves like a manually-maintained price.
"""
from __future__ import annotations

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.assets.insurance import Insurance
from app.models.assets.insurance_value_history import (
    InsuranceValueCreate,
    InsuranceValueHistory,
    InsuranceValueMonthRead,
)


def select_month_surrender_value(
    session: Session, insurance_id: str, vesting_month: str
) -> InsuranceValueHistory | None:
    """Latest recorded surrender value for a policy on or before ``vesting_month``.

    Carries a value forward: a record entered in an earlier month applies until
    a newer one is entered. Returns ``None`` when nothing has ever been recorded
    for the policy, so callers can fall back to the premium-based estimate.
    """
    stmt = (
        select(InsuranceValueHistory)
        .where(InsuranceValueHistory.insurance_id == insurance_id)
        .where(InsuranceValueHistory.vesting_month <= vesting_month)
        .order_by(InsuranceValueHistory.vesting_month.desc())
    )
    return session.exec(stmt).first()


def list_month_insurance_values(
    session: Session, vesting_month: str
) -> list[InsuranceValueMonthRead]:
    """Per-policy surrender value as of a month (latest recorded, carried forward).

    Every policy is emitted so the UI can show which ones still need a value:
    ``recorded`` is True only when the value was entered in this exact month.
    """
    policies = list(session.exec(select(Insurance)).all())
    out: list[InsuranceValueMonthRead] = []
    for p in policies:
        row = select_month_surrender_value(session, p.insurance_id, vesting_month)
        out.append(
            InsuranceValueMonthRead(
                insurance_id=p.insurance_id,
                insurance_name=p.insurance_name,
                surrender_value=row.surrender_value if row is not None else None,
                vesting_month=row.vesting_month if row is not None else None,
                recorded=bool(row is not None and row.vesting_month == vesting_month),
            )
        )
    return out


def upsert_insurance_value(
    session: Session, payload: InsuranceValueCreate
) -> InsuranceValueHistory:
    """Insert or update the surrender value for a (policy, month).

    Idempotent on the composite PK: re-recording a month overwrites it. 404s
    when the policy does not exist so a typo can't create an orphan record.
    """
    if session.get(Insurance, payload.insurance_id) is None:
        raise HTTPException(
            status_code=404, detail=f"Insurance not found: {payload.insurance_id}"
        )
    existing = session.get(
        InsuranceValueHistory, (payload.insurance_id, payload.vesting_month)
    )
    if existing is not None:
        existing.surrender_value = payload.surrender_value
        existing.memo = payload.memo
        row = existing
    else:
        row = InsuranceValueHistory(**payload.model_dump())
    session.add(row)
    session.commit()
    session.refresh(row)
    return row
