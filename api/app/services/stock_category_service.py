"""Stock category dictionary service (Assets domain, session-as-parameter).

``Stock_Journal.category_id`` references ``Stock_Category.category_id``. A
category that is still referenced by any holding cannot be hard-deleted; retire
it via ``in_use = "N"`` instead so existing holdings keep their classification.
"""
from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import func
from sqlmodel import Session, select

from app.models.assets.stock import StockJournal
from app.models.assets.stock_category import (
    StockCategory,
    StockCategoryCreate,
    StockCategoryUpdate,
)


def _next_category_id(session: Session) -> str:
    """Generate the next ``SC-NNN`` id from the current max numeric suffix."""
    ids = session.exec(select(StockCategory.category_id)).all()
    max_n = 0
    for cid in ids:
        if cid and cid.startswith("SC-") and cid[3:].isdigit():
            max_n = max(max_n, int(cid[3:]))
    return f"SC-{max_n + 1:03d}"


def list_stock_categories(
    session: Session, in_use: str | None = None
) -> list[StockCategory]:
    """Return categories ordered for dropdown rendering, optional in_use filter."""
    statement = select(StockCategory)
    if in_use:
        statement = statement.where(StockCategory.in_use == in_use)
    statement = statement.order_by(
        StockCategory.category_index.asc(), StockCategory.category_id.asc()
    )
    return list(session.exec(statement).all())


def create_stock_category(
    session: Session, data: StockCategoryCreate
) -> StockCategory:
    """Insert a category with a server-generated ``category_id``; auto-fill index."""
    payload = data.model_dump()
    if payload.get("category_index") is None:
        max_idx = session.exec(select(func.max(StockCategory.category_index))).first() or 0
        payload["category_index"] = (max_idx or 0) + 1
    payload["category_id"] = _next_category_id(session)
    row = StockCategory(**payload)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def update_stock_category(
    session: Session, category_id: str, data: StockCategoryUpdate
) -> StockCategory:
    row = session.get(StockCategory, category_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Stock category not found: {category_id}")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def delete_stock_category(session: Session, category_id: str) -> None:
    """Hard-delete an unused category; refuse (409) if any holding references it."""
    row = session.get(StockCategory, category_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Stock category not found: {category_id}")
    referenced = session.exec(
        select(StockJournal).where(StockJournal.category_id == category_id)
    ).first()
    if referenced is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Stock category {category_id} is in use by one or more holdings; "
                "retire it with in_use='N' instead of deleting."
            ),
        )
    session.delete(row)
    session.commit()
