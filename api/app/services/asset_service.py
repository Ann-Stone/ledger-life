"""Asset domain service functions (flat, session-as-parameter)."""
from __future__ import annotations

from dateutil import parser as date_parser
from fastapi import HTTPException
from sqlalchemy import func
from sqlmodel import Session, select

from app.models.assets.estate import (
    Estate,
    EstateCreate,
    EstateJournal,
    EstateJournalCreate,
    EstateJournalUpdate,
    EstateUpdate,
)
from app.models.assets.insurance import (
    Insurance,
    InsuranceCreate,
    InsuranceJournal,
    InsuranceJournalCreate,
    InsuranceJournalUpdate,
    InsuranceUpdate,
)
from app.models.assets.loan import (
    Loan,
    LoanCreate,
    LoanJournal,
    LoanJournalCreate,
    LoanJournalUpdate,
    LoanSelectionRead,
    LoanUpdate,
)
from app.models.assets.other_asset import (
    OtherAsset,
    OtherAssetCreate,
    OtherAssetItem,
    OtherAssetUpdate,
)
from app.models.assets.stock import (
    StockDetail,
    StockDetailCreate,
    StockDetailUpdate,
    StockJournal,
    StockJournalCreate,
    StockJournalUpdate,
)


# ---------- helpers ----------


def _normalize_ymd(value: str | None) -> str | None:
    """Parse an ISO 8601 (or YYYYMMDD) date string and return ``YYYYMMDD``.

    Returns ``None`` when the input is ``None``. Raises ``HTTPException(422)``
    on unparsable input so the caller surfaces a validation error.
    """
    if value is None:
        return None
    try:
        parsed = date_parser.parse(value)
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=f"Invalid date: {value!r}") from exc
    return parsed.strftime("%Y%m%d")


# ---------- Stock ----------


def list_stocks(session: Session, asset_id: str) -> list[StockJournal]:
    statement = select(StockJournal).where(StockJournal.asset_id == asset_id)
    return list(session.exec(statement).all())


def create_stock(session: Session, payload: StockJournalCreate) -> StockJournal:
    existing = session.exec(
        select(StockJournal).where(StockJournal.stock_id == payload.stock_id)
    ).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail=f"Duplicate stock_id: {payload.stock_id}")
    holding = StockJournal(**payload.model_dump())
    session.add(holding)
    session.commit()
    session.refresh(holding)
    return holding


def update_stock(session: Session, stock_id: str, payload: StockJournalUpdate) -> StockJournal:
    holding = session.get(StockJournal, stock_id)
    if holding is None:
        raise HTTPException(status_code=404, detail=f"Stock not found: {stock_id}")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(holding, field, value)
    session.add(holding)
    session.commit()
    session.refresh(holding)
    return holding


def delete_stock(session: Session, stock_id: str) -> None:
    holding = session.get(StockJournal, stock_id)
    if holding is None:
        raise HTTPException(status_code=404, detail=f"Stock not found: {stock_id}")
    session.delete(holding)
    session.commit()


def list_stock_details(session: Session, stock_id: str) -> list[StockDetail]:
    statement = (
        select(StockDetail)
        .where(StockDetail.stock_id == stock_id)
        .order_by(StockDetail.excute_date.asc(), StockDetail.distinct_number.asc())
    )
    return list(session.exec(statement).all())


def create_stock_detail(
    session: Session, stock_id: str, payload: StockDetailCreate
) -> StockDetail:
    if payload.stock_id != stock_id:
        raise HTTPException(
            status_code=422,
            detail=f"payload.stock_id={payload.stock_id} does not match path stock_id={stock_id}",
        )
    holding = session.get(StockJournal, stock_id)
    if holding is None:
        raise HTTPException(status_code=404, detail=f"Stock not found: {stock_id}")
    detail = StockDetail(**payload.model_dump())
    session.add(detail)
    session.commit()
    session.refresh(detail)
    return detail


def update_stock_detail(
    session: Session, distinct_number: int, payload: StockDetailUpdate
) -> StockDetail:
    detail = session.get(StockDetail, distinct_number)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Stock detail not found: {distinct_number}")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(detail, field, value)
    session.add(detail)
    session.commit()
    session.refresh(detail)
    return detail


def delete_stock_detail(session: Session, distinct_number: int) -> None:
    detail = session.get(StockDetail, distinct_number)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Stock detail not found: {distinct_number}")
    session.delete(detail)
    session.commit()


# ---------- Insurance ----------


def list_insurances(session: Session, asset_id: str) -> list[Insurance]:
    statement = select(Insurance).where(Insurance.asset_id == asset_id)
    return list(session.exec(statement).all())


def create_insurance(session: Session, payload: InsuranceCreate) -> Insurance:
    existing = session.get(Insurance, payload.insurance_id)
    if existing is not None:
        raise HTTPException(status_code=409, detail=f"Duplicate insurance_id: {payload.insurance_id}")
    data = payload.model_dump()
    data["start_date"] = _normalize_ymd(data["start_date"])
    data["end_date"] = _normalize_ymd(data["end_date"])
    row = Insurance(**data)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def update_insurance(
    session: Session, insurance_id: str, payload: InsuranceUpdate
) -> Insurance:
    row = session.get(Insurance, insurance_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Insurance not found: {insurance_id}")
    data = payload.model_dump(exclude_unset=True)
    if "start_date" in data:
        data["start_date"] = _normalize_ymd(data["start_date"])
    if "end_date" in data:
        data["end_date"] = _normalize_ymd(data["end_date"])
    for field, value in data.items():
        setattr(row, field, value)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def delete_insurance(session: Session, insurance_id: str) -> None:
    row = session.get(Insurance, insurance_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Insurance not found: {insurance_id}")
    session.delete(row)
    session.commit()


def list_insurance_details(session: Session, insurance_id: str) -> list[InsuranceJournal]:
    statement = (
        select(InsuranceJournal)
        .where(InsuranceJournal.insurance_id == insurance_id)
        .order_by(InsuranceJournal.excute_date.asc(), InsuranceJournal.distinct_number.asc())
    )
    return list(session.exec(statement).all())


def create_insurance_detail(
    session: Session, insurance_id: str, payload: InsuranceJournalCreate
) -> InsuranceJournal:
    if payload.insurance_id != insurance_id:
        raise HTTPException(
            status_code=422,
            detail="payload.insurance_id does not match path insurance_id",
        )
    if session.get(Insurance, insurance_id) is None:
        raise HTTPException(status_code=404, detail=f"Insurance not found: {insurance_id}")
    data = payload.model_dump()
    data["excute_date"] = _normalize_ymd(data["excute_date"])
    detail = InsuranceJournal(**data)
    session.add(detail)
    session.commit()
    session.refresh(detail)
    return detail


def update_insurance_detail(
    session: Session, distinct_number: int, payload: InsuranceJournalUpdate
) -> InsuranceJournal:
    detail = session.get(InsuranceJournal, distinct_number)
    if detail is None:
        raise HTTPException(
            status_code=404, detail=f"Insurance detail not found: {distinct_number}"
        )
    data = payload.model_dump(exclude_unset=True)
    if "excute_date" in data:
        data["excute_date"] = _normalize_ymd(data["excute_date"])
    for field, value in data.items():
        setattr(detail, field, value)
    session.add(detail)
    session.commit()
    session.refresh(detail)
    return detail


def delete_insurance_detail(session: Session, distinct_number: int) -> None:
    detail = session.get(InsuranceJournal, distinct_number)
    if detail is None:
        raise HTTPException(
            status_code=404, detail=f"Insurance detail not found: {distinct_number}"
        )
    session.delete(detail)
    session.commit()


# ---------- Estate ----------


def list_estates(session: Session, asset_id: str) -> list[Estate]:
    statement = select(Estate).where(Estate.asset_id == asset_id)
    return list(session.exec(statement).all())


def create_estate(session: Session, payload: EstateCreate) -> Estate:
    existing = session.get(Estate, payload.estate_id)
    if existing is not None:
        raise HTTPException(status_code=409, detail=f"Duplicate estate_id: {payload.estate_id}")
    data = payload.model_dump()
    data["obtain_date"] = _normalize_ymd(data["obtain_date"])
    row = Estate(**data)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def update_estate(session: Session, estate_id: str, payload: EstateUpdate) -> Estate:
    row = session.get(Estate, estate_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Estate not found: {estate_id}")
    data = payload.model_dump(exclude_unset=True)
    if "obtain_date" in data:
        data["obtain_date"] = _normalize_ymd(data["obtain_date"])
    for field, value in data.items():
        setattr(row, field, value)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def delete_estate(session: Session, estate_id: str) -> None:
    row = session.get(Estate, estate_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Estate not found: {estate_id}")
    session.delete(row)
    session.commit()


def list_estate_details(session: Session, estate_id: str) -> list[EstateJournal]:
    statement = (
        select(EstateJournal)
        .where(EstateJournal.estate_id == estate_id)
        .order_by(EstateJournal.excute_date.asc(), EstateJournal.distinct_number.asc())
    )
    return list(session.exec(statement).all())


def create_estate_detail(
    session: Session, estate_id: str, payload: EstateJournalCreate
) -> EstateJournal:
    if payload.estate_id != estate_id:
        raise HTTPException(
            status_code=422,
            detail="payload.estate_id does not match path estate_id",
        )
    if session.get(Estate, estate_id) is None:
        raise HTTPException(status_code=404, detail=f"Estate not found: {estate_id}")
    data = payload.model_dump()
    data["excute_date"] = _normalize_ymd(data["excute_date"])
    detail = EstateJournal(**data)
    session.add(detail)
    session.commit()
    session.refresh(detail)
    return detail


def update_estate_detail(
    session: Session, distinct_number: int, payload: EstateJournalUpdate
) -> EstateJournal:
    detail = session.get(EstateJournal, distinct_number)
    if detail is None:
        raise HTTPException(
            status_code=404, detail=f"Estate detail not found: {distinct_number}"
        )
    data = payload.model_dump(exclude_unset=True)
    if "excute_date" in data:
        data["excute_date"] = _normalize_ymd(data["excute_date"])
    for field, value in data.items():
        setattr(detail, field, value)
    session.add(detail)
    session.commit()
    session.refresh(detail)
    return detail


def delete_estate_detail(session: Session, distinct_number: int) -> None:
    detail = session.get(EstateJournal, distinct_number)
    if detail is None:
        raise HTTPException(
            status_code=404, detail=f"Estate detail not found: {distinct_number}"
        )
    session.delete(detail)
    session.commit()


# ---------- Loan ----------


def list_loans(session: Session) -> list[Loan]:
    statement = select(Loan).order_by(Loan.loan_index.asc())
    return list(session.exec(statement).all())


def get_loan(session: Session, loan_id: str) -> Loan:
    row = session.get(Loan, loan_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Loan not found: {loan_id}")
    return row


def list_loan_selection(session: Session) -> list[LoanSelectionRead]:
    rows = session.exec(select(Loan).order_by(Loan.loan_index.asc())).all()
    return [LoanSelectionRead(loan_id=r.loan_id, loan_name=r.loan_name) for r in rows]


def create_loan(session: Session, payload: LoanCreate) -> Loan:
    existing = session.get(Loan, payload.loan_id)
    if existing is not None:
        raise HTTPException(status_code=409, detail=f"Duplicate loan_id: {payload.loan_id}")
    data = payload.model_dump()
    data["apply_date"] = _normalize_ymd(data["apply_date"])
    data["grace_expire_date"] = _normalize_ymd(data.get("grace_expire_date"))
    data["repayed"] = 0.0
    row = Loan(**data)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def update_loan(session: Session, loan_id: str, payload: LoanUpdate) -> Loan:
    row = session.get(Loan, loan_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Loan not found: {loan_id}")
    data = payload.model_dump(exclude_unset=True)
    # repayed is server-computed; ignore if client tries to override.
    data.pop("repayed", None)
    if "apply_date" in data:
        data["apply_date"] = _normalize_ymd(data["apply_date"])
    if "grace_expire_date" in data:
        data["grace_expire_date"] = _normalize_ymd(data["grace_expire_date"])
    for field, value in data.items():
        setattr(row, field, value)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def delete_loan(session: Session, loan_id: str) -> None:
    row = session.get(Loan, loan_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Loan not found: {loan_id}")
    session.delete(row)
    session.commit()


def _recalculate_repayed(session: Session, loan_id: str) -> None:
    total = session.exec(
        select(func.coalesce(func.sum(LoanJournal.excute_price), 0.0))
        .where(LoanJournal.loan_id == loan_id)
        .where(LoanJournal.loan_excute_type == "principal")
    ).one()
    row = session.get(Loan, loan_id)
    if row is None:
        return
    row.repayed = float(total or 0.0)
    session.add(row)
    session.commit()
    session.refresh(row)


def list_loan_details(session: Session, loan_id: str) -> list[LoanJournal]:
    statement = (
        select(LoanJournal)
        .where(LoanJournal.loan_id == loan_id)
        .order_by(LoanJournal.excute_date.asc(), LoanJournal.distinct_number.asc())
    )
    return list(session.exec(statement).all())


def create_loan_detail(
    session: Session, loan_id: str, payload: LoanJournalCreate
) -> LoanJournal:
    if payload.loan_id != loan_id:
        raise HTTPException(
            status_code=422,
            detail="payload.loan_id does not match path loan_id",
        )
    if session.get(Loan, loan_id) is None:
        raise HTTPException(status_code=404, detail=f"Loan not found: {loan_id}")
    data = payload.model_dump()
    data["excute_date"] = _normalize_ymd(data["excute_date"])
    detail = LoanJournal(**data)
    session.add(detail)
    session.commit()
    session.refresh(detail)
    _recalculate_repayed(session, loan_id)
    session.refresh(detail)
    return detail


def update_loan_detail(
    session: Session, distinct_number: int, payload: LoanJournalUpdate
) -> LoanJournal:
    detail = session.get(LoanJournal, distinct_number)
    if detail is None:
        raise HTTPException(
            status_code=404, detail=f"Loan detail not found: {distinct_number}"
        )
    data = payload.model_dump(exclude_unset=True)
    if "excute_date" in data:
        data["excute_date"] = _normalize_ymd(data["excute_date"])
    for field, value in data.items():
        setattr(detail, field, value)
    session.add(detail)
    session.commit()
    session.refresh(detail)
    _recalculate_repayed(session, detail.loan_id)
    session.refresh(detail)
    return detail


def delete_loan_detail(session: Session, distinct_number: int) -> None:
    detail = session.get(LoanJournal, distinct_number)
    if detail is None:
        raise HTTPException(
            status_code=404, detail=f"Loan detail not found: {distinct_number}"
        )
    loan_id = detail.loan_id
    session.delete(detail)
    session.commit()
    _recalculate_repayed(session, loan_id)


# ---------- OtherAsset ----------


def list_other_assets(session: Session) -> list[OtherAsset]:
    statement = select(OtherAsset).order_by(OtherAsset.asset_index.asc())
    return list(session.exec(statement).all())


def list_other_asset_items(session: Session) -> list[OtherAssetItem]:
    rows = session.exec(select(OtherAsset.asset_type).distinct()).all()
    return [OtherAssetItem(asset_type=r) for r in rows]


def create_other_asset(session: Session, payload: OtherAssetCreate) -> OtherAsset:
    existing = session.get(OtherAsset, payload.asset_id)
    if existing is not None:
        raise HTTPException(status_code=409, detail=f"Duplicate asset_id: {payload.asset_id}")
    data = payload.model_dump()
    if data.get("asset_index") is None:
        max_idx = session.exec(select(func.max(OtherAsset.asset_index))).first()
        data["asset_index"] = (max_idx or 0) + 1
    row = OtherAsset(**data)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def update_other_asset(
    session: Session, asset_id: str, payload: OtherAssetUpdate
) -> OtherAsset:
    row = session.get(OtherAsset, asset_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"OtherAsset not found: {asset_id}")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def delete_other_asset(session: Session, asset_id: str) -> None:
    row = session.get(OtherAsset, asset_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"OtherAsset not found: {asset_id}")
    session.delete(row)
    session.commit()
