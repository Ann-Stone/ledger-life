"""Settings domain service functions (flat, session-as-parameter)."""
from __future__ import annotations

from collections import defaultdict
from datetime import date

from dateutil import parser as date_parser
from fastapi import HTTPException
from sqlalchemy import func, or_
from sqlmodel import Session, select

from app.models.settings.account import Account, AccountCreate, AccountUpdate
from app.models.settings.alarm import Alarm, AlarmCreate, AlarmUpdate
from app.models.settings.budget import Budget, BudgetCreate, BudgetUpdate
from app.models.settings.credit_card import CreditCard, CreditCardCreate, CreditCardUpdate
from app.models.monthly_report.journal import Journal
from app.models.settings.code_data import (
    CodeData,
    CodeDataCreate,
    CodeDataUpdate,
    CodeWithSubs,
)


# ---------- Account ----------


def list_accounts(
    session: Session,
    name: str | None = None,
    account_type: str | None = None,
    in_use: str | None = None,
) -> list[Account]:
    """Return accounts with optional substring/equality filters."""
    statement = select(Account)
    if name:
        statement = statement.where(Account.name.contains(name))
    if account_type:
        statement = statement.where(Account.account_type == account_type)
    if in_use:
        statement = statement.where(Account.in_use == in_use)
    return list(session.exec(statement).all())


def list_accounts_selection(session: Session) -> list[Account]:
    """Return active accounts ordered for dropdown rendering."""
    statement = (
        select(Account)
        .where(Account.in_use == "Y")
        .order_by(Account.account_index.asc(), Account.id.asc())
    )
    return list(session.exec(statement).all())


def create_account(session: Session, data: AccountCreate) -> Account:
    """Insert a new Account; auto-fill ``account_index`` and reject duplicate ``account_id``."""
    existing = session.exec(
        select(Account).where(Account.account_id == data.account_id)
    ).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail=f"Duplicate account_id: {data.account_id}")

    payload = data.model_dump()
    if payload.get("account_index") is None:
        max_idx = session.exec(select(func.max(Account.account_index))).first() or 0
        payload["account_index"] = (max_idx or 0) + 1

    account = Account(**payload)
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


def update_account(session: Session, id: int, data: AccountUpdate) -> Account:
    account = session.get(Account, id)
    if account is None:
        raise HTTPException(status_code=404, detail=f"Account not found: {id}")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(account, field, value)
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


def delete_account(session: Session, id: int) -> None:
    account = session.get(Account, id)
    if account is None:
        raise HTTPException(status_code=404, detail=f"Account not found: {id}")
    session.delete(account)
    session.commit()


# ---------- CodeData (main + sub) ----------


_BUDGET_TRIGGER_TYPES = {"Fixed", "Floating"}


def _get_main_code(session: Session, code_id: str) -> CodeData:
    row = session.get(CodeData, code_id)
    if row is None or row.parent_id is not None:
        raise HTTPException(status_code=404, detail=f"Main code not found: {code_id}")
    return row


def _get_sub_code(session: Session, code_id: str) -> CodeData:
    row = session.get(CodeData, code_id)
    if row is None or row.parent_id is None:
        raise HTTPException(status_code=404, detail=f"Sub-code not found: {code_id}")
    return row


def list_main_codes(session: Session) -> list[CodeData]:
    statement = (
        select(CodeData)
        .where(CodeData.parent_id.is_(None))
        .order_by(CodeData.code_index.asc(), CodeData.code_id.asc())
    )
    return list(session.exec(statement).all())


def list_codes_with_sub_codes(session: Session) -> list[CodeWithSubs]:
    mains = list_main_codes(session)
    sub_statement = (
        select(CodeData)
        .where(CodeData.parent_id.is_not(None))
        .order_by(CodeData.code_index.asc(), CodeData.code_id.asc())
    )
    subs = list(session.exec(sub_statement).all())
    by_parent: dict[str, list[CodeData]] = {}
    for s in subs:
        by_parent.setdefault(s.parent_id, []).append(s)
    return [
        CodeWithSubs(
            **m.model_dump(),
            sub_codes=[s.model_dump() for s in by_parent.get(m.code_id, [])],
        )
        for m in mains
    ]


def _autofill_code_index(session: Session, payload: dict) -> dict:
    if payload.get("code_index") is None:
        max_idx = session.exec(select(func.max(CodeData.code_index))).first() or 0
        payload["code_index"] = (max_idx or 0) + 1
    return payload


def create_main_code(session: Session, data: CodeDataCreate) -> CodeData:
    if session.get(CodeData, data.code_id) is not None:
        raise HTTPException(status_code=409, detail=f"Duplicate code_id: {data.code_id}")

    payload = _autofill_code_index(session, data.model_dump())
    payload["parent_id"] = None
    code = CodeData(**payload)
    session.add(code)

    if data.code_type in _BUDGET_TRIGGER_TYPES:
        year = str(date.today().year)
        budget = Budget(
            budget_year=year,
            category_code=data.code_id,
            category_name=data.name,
            code_type=data.code_type,
            **{f"expected{m:02d}": 0.0 for m in range(1, 13)},
        )
        session.add(budget)

    session.commit()
    session.refresh(code)
    return code


def update_main_code(session: Session, code_id: str, data: CodeDataUpdate) -> CodeData:
    code = _get_main_code(session, code_id)
    update_data = data.model_dump(exclude_unset=True)
    update_data.pop("parent_id", None)  # cannot turn a main into a sub via update
    for k, v in update_data.items():
        setattr(code, k, v)
    session.add(code)
    session.commit()
    session.refresh(code)
    return code


def delete_main_code(session: Session, code_id: str) -> None:
    code = _get_main_code(session, code_id)
    session.delete(code)
    session.commit()


def list_sub_codes(session: Session, parent_id: str) -> list[CodeData]:
    _get_main_code(session, parent_id)
    statement = (
        select(CodeData)
        .where(CodeData.parent_id == parent_id)
        .order_by(CodeData.code_index.asc(), CodeData.code_id.asc())
    )
    return list(session.exec(statement).all())


def create_sub_code(session: Session, data: CodeDataCreate) -> CodeData:
    if not data.parent_id:
        raise HTTPException(status_code=422, detail="parent_id is required for sub-codes")
    _get_main_code(session, data.parent_id)
    if session.get(CodeData, data.code_id) is not None:
        raise HTTPException(status_code=409, detail=f"Duplicate code_id: {data.code_id}")

    payload = _autofill_code_index(session, data.model_dump())
    code = CodeData(**payload)
    session.add(code)
    session.commit()
    session.refresh(code)
    return code


def update_sub_code(session: Session, code_id: str, data: CodeDataUpdate) -> CodeData:
    code = _get_sub_code(session, code_id)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(code, k, v)
    session.add(code)
    session.commit()
    session.refresh(code)
    return code


def delete_sub_code(session: Session, code_id: str) -> None:
    code = _get_sub_code(session, code_id)
    session.delete(code)
    session.commit()


# ---------- Budget ----------


def list_budgets_by_year(session: Session, year: int) -> list[Budget]:
    statement = (
        select(Budget)
        .where(Budget.budget_year == str(year))
        .order_by(Budget.category_code.asc())
    )
    return list(session.exec(statement).all())


def list_budget_year_range(session: Session) -> list[int]:
    rows = session.exec(
        select(Budget.budget_year).distinct().order_by(Budget.budget_year.asc())
    ).all()
    return [int(r) for r in rows]


def bulk_update_budgets(session: Session, items: list[BudgetUpdate]) -> list[Budget]:
    rows: list[Budget] = []
    for item in items:
        budget = session.get(Budget, (item.budget_year, item.category_code))
        if budget is None:
            session.rollback()
            raise HTTPException(
                status_code=404,
                detail=f"Budget not found: {item.budget_year}/{item.category_code}",
            )
        update_data = item.model_dump(
            exclude_unset=True, exclude={"budget_year", "category_code"}
        )
        for k, v in update_data.items():
            setattr(budget, k, v)
        session.add(budget)
        rows.append(budget)
    session.commit()
    for r in rows:
        session.refresh(r)
    return rows


# ---------- CreditCard ----------


def list_credit_cards(
    session: Session,
    card_name: str | None = None,
    in_use: str | None = None,
) -> list[CreditCard]:
    statement = select(CreditCard)
    if card_name:
        statement = statement.where(CreditCard.card_name.contains(card_name))
    if in_use:
        statement = statement.where(CreditCard.in_use == in_use)
    statement = statement.order_by(
        CreditCard.credit_card_index.asc(), CreditCard.credit_card_id.asc()
    )
    return list(session.exec(statement).all())


def create_credit_card(session: Session, data: CreditCardCreate) -> CreditCard:
    if session.get(CreditCard, data.credit_card_id) is not None:
        raise HTTPException(
            status_code=409, detail=f"Duplicate credit_card_id: {data.credit_card_id}"
        )
    payload = data.model_dump()
    if payload.get("credit_card_index") is None:
        max_idx = session.exec(select(func.max(CreditCard.credit_card_index))).first() or 0
        payload["credit_card_index"] = (max_idx or 0) + 1
    card = CreditCard(**payload)
    session.add(card)
    session.commit()
    session.refresh(card)
    return card


def update_credit_card(
    session: Session, credit_card_id: str, data: CreditCardUpdate
) -> CreditCard:
    card = session.get(CreditCard, credit_card_id)
    if card is None:
        raise HTTPException(status_code=404, detail=f"Credit card not found: {credit_card_id}")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(card, k, v)
    session.add(card)
    session.commit()
    session.refresh(card)
    return card


def delete_credit_card(session: Session, credit_card_id: str) -> None:
    card = session.get(CreditCard, credit_card_id)
    if card is None:
        raise HTTPException(status_code=404, detail=f"Credit card not found: {credit_card_id}")
    session.delete(card)
    session.commit()


def _median(values: list[float]) -> float:
    """Median of a list; mean of the two middle values for even counts; 0 when empty."""
    if not values:
        return 0.0
    ordered = sorted(values)
    n = len(ordered)
    mid = n // 2
    if n % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def suggest_budget(session: Session, year: int) -> list[Budget]:
    """Compute (without persisting) suggested Budget rows for ``year``.

    Uses the last up-to-3 years of Journal spending for each active Fixed/Floating
    main category, keyed by ``action_main`` (the category code). Ordinary categories
    get a robust per-calendar-month estimate (median across the years that have data,
    so recurring seasonality survives while one-off month spikes are damped).
    Annual-event categories instead get a single ``annual_amount`` envelope = median
    of the years' annual totals. Transfer/invest/income journals are excluded because
    only Fixed/Floating categories are emitted.
    """
    year_str = str(year)
    years = [year - 1, year - 2, year - 3]
    lo, hi = f"{year - 3}01", f"{year - 1}12"

    codes = session.exec(
        select(CodeData).where(
            CodeData.parent_id.is_(None),
            CodeData.code_type.in_(_BUDGET_TRIGGER_TYPES),
            CodeData.in_use == "Y",
        )
    ).all()

    journals = session.exec(
        select(Journal).where(Journal.vesting_month >= lo, Journal.vesting_month <= hi)
    ).all()

    # sums[code_id][year][month] = sum of |spending|
    sums: dict[str, dict[int, dict[int, float]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(float))
    )
    for j in journals:
        vm = j.vesting_month or ""
        if len(vm) != 6:
            continue
        y, m = int(vm[:4]), int(vm[4:6])
        sums[j.action_main][y][m] += abs(j.spending or 0.0)

    rows: list[Budget] = []
    for code in sorted(codes, key=lambda c: c.code_id):
        per_year = sums.get(code.code_id, {})
        present_years = [y for y in years if y in per_year]

        if code.is_annual_event:
            totals = [sum(per_year[y].values()) for y in present_years]
            rows.append(
                Budget(
                    budget_year=year_str,
                    category_code=code.code_id,
                    category_name=code.name,
                    code_type=code.code_type,
                    annual_amount=round(_median(totals), 2),
                    **{f"expected{m:02d}": 0.0 for m in range(1, 13)},
                )
            )
        else:
            monthly = {
                f"expected{m:02d}": round(
                    _median([per_year[y].get(m, 0.0) for y in present_years]), 2
                )
                for m in range(1, 13)
            }
            rows.append(
                Budget(
                    budget_year=year_str,
                    category_code=code.code_id,
                    category_name=code.name,
                    code_type=code.code_type,
                    annual_amount=None,
                    **monthly,
                )
            )
    return rows


def apply_budget(session: Session, items: list[BudgetCreate]) -> list[Budget]:
    """Upsert full budget rows (insert when missing) by (budget_year, category_code)."""
    for item in items:
        data = item.model_dump()
        existing = session.get(Budget, (item.budget_year, item.category_code))
        if existing is not None:
            for k, v in data.items():
                setattr(existing, k, v)
            session.add(existing)
        else:
            session.add(Budget(**data))
    session.commit()
    return [
        row
        for item in items
        if (row := session.get(Budget, (item.budget_year, item.category_code))) is not None
    ]


# ---------- Alarm ----------


def _normalize_due_date(value: str | None) -> str | None:
    if value is None or value == "":
        return None
    try:
        dt = date_parser.parse(value)
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=422, detail="Unparseable due_date") from e
    return dt.strftime("%Y%m%d")


def list_alarms(session: Session) -> list[Alarm]:
    statement = select(Alarm).order_by(Alarm.alarm_id.asc())
    return list(session.exec(statement).all())


def list_alarms_by_date(session: Session, date: str) -> list[Alarm]:
    statement = select(Alarm).where(
        or_(Alarm.alarm_date == date, Alarm.alarm_date.like(f"%{date}"))
    )
    return list(session.exec(statement).all())


def create_alarm(session: Session, data: AlarmCreate) -> Alarm:
    payload = data.model_dump()
    payload["due_date"] = _normalize_due_date(payload.get("due_date"))
    alarm = Alarm(**payload)
    session.add(alarm)
    session.commit()
    session.refresh(alarm)
    return alarm


def update_alarm(session: Session, alarm_id: int, data: AlarmUpdate) -> Alarm:
    alarm = session.get(Alarm, alarm_id)
    if alarm is None:
        raise HTTPException(status_code=404, detail=f"Alarm not found: {alarm_id}")
    update_data = data.model_dump(exclude_unset=True)
    if "due_date" in update_data:
        update_data["due_date"] = _normalize_due_date(update_data["due_date"])
    for k, v in update_data.items():
        setattr(alarm, k, v)
    session.add(alarm)
    session.commit()
    session.refresh(alarm)
    return alarm


def delete_alarm(session: Session, alarm_id: int) -> None:
    alarm = session.get(Alarm, alarm_id)
    if alarm is None:
        raise HTTPException(status_code=404, detail=f"Alarm not found: {alarm_id}")
    session.delete(alarm)
    session.commit()
