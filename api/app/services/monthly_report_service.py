"""Monthly Report domain service functions (flat, session-as-parameter)."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.monthly_report.analytics import (
    ExpenditureBudgetResponse,
    ExpenditureBudgetRow,
    ExpenditureRatioItem,
    ExpenditureRatioResponse,
    InvestRatioItem,
    InvestRatioResponse,
    LiabilityItem,
    LiabilityResponse,
    UncategorizedMonthCount,
    UncategorizedSummaryResponse,
)
from app.models.assets.estate import Estate, EstateJournal
from app.models.assets.insurance import Insurance, InsuranceJournal
from app.models.assets.loan import Loan, LoanJournal
from app.models.assets.stock import StockDetail, StockJournal
from app.models.monthly_report.journal import (
    Journal,
    JournalCreate,
    JournalUpdate,
)
from app.models.monthly_report.journal_composite import (
    JournalEstateTransactionCreate,
    JournalEstateTransactionUpdate,
    JournalInsuranceTransactionCreate,
    JournalInsuranceTransactionUpdate,
    JournalLoanTransactionCreate,
    JournalLoanTransactionUpdate,
    JournalStockTransactionCreate,
    JournalStockTransactionUpdate,
)
from app.models.settings.account import Account
from app.models.settings.budget import Budget
from app.models.settings.code_data import CodeData
from app.models.settings.credit_card import CreditCard
from app.services.expense_netting import floor_expense, floor_income
from app.services.fx_lookup import BASE_CURRENCY, fx_rate_for_month
from app.services.loan_journal_amounts import loan_repayment_by_bucket
from app.services.journal_types import (
    EXPENSE_MAIN_TYPES,
    FINANCING_MAIN_TYPES,
    INCOME_MAIN_TYPES,
    INVEST_MAIN_TYPES,
    TRANSFER_MAIN_TYPES,
    is_uncategorized,
    norm_type,
)


def normalize_spend_date(value: str) -> str:
    """Accept ISO 8601 or `YYYYMMDD` and return canonical `YYYYMMDD`."""
    if not isinstance(value, str) or not value:
        raise ValueError(f"Invalid spend_date: {value!r}")
    if len(value) == 8 and value.isdigit():
        # Validate it's a real date.
        try:
            datetime.strptime(value, "%Y%m%d")
        except ValueError as exc:
            raise ValueError(f"Invalid spend_date: {value!r}") from exc
        return value
    try:
        # Strip Z suffix that fromisoformat doesn't accept on older Python.
        text = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"Invalid spend_date: {value!r}") from exc
    return parsed.strftime("%Y%m%d")


def list_journals_by_month(session: Session, vesting_month: str) -> list[Journal]:
    statement = (
        select(Journal)
        .where(Journal.vesting_month == vesting_month)
        .order_by(Journal.spend_date.asc(), Journal.distinct_number.asc())
    )
    return list(session.exec(statement).all())


def _account_by_spend_way(session: Session, spend_way: str) -> Account | None:
    """Resolve an Account from a Journal.spend_way value.

    spend_way carries the account's primary key (``Account.id``) stringified.
    Returns ``None`` for non-numeric or unknown values so callers can fall back
    gracefully (e.g. keep the base currency in ``compute_gain_loss``).
    """
    try:
        pk = int(spend_way)
    except (TypeError, ValueError):
        return None
    return session.get(Account, pk)


def compute_gain_loss(session: Session, journals: list[Journal]) -> float:
    """Signed sum of journal spending across the month, FX-converted to base.

    This is genuine month P/L (net cash movement), so it intentionally stays
    signed — unlike the expense reports, which net per category then floor at 0.
    A category that nets to an inflow here legitimately raises the month's P/L.
    """
    if not journals:
        return 0.0
    total = 0.0
    fx_cache: dict[tuple[str, str], float] = {}
    for j in journals:
        fx_code = BASE_CURRENCY
        if j.spend_way_table == "Account":
            account = _account_by_spend_way(session, j.spend_way)
            if account is not None and account.fx_code:
                fx_code = account.fx_code
        rate = 1.0
        if fx_code != BASE_CURRENCY:
            key = (fx_code, j.vesting_month)
            if key not in fx_cache:
                fx_cache[key] = fx_rate_for_month(session, fx_code, j.vesting_month)
            rate = fx_cache[key]
        total += j.spending * rate
    return round(total, 2)


def create_journal(session: Session, payload: JournalCreate) -> Journal:
    data = payload.model_dump()
    data["spend_date"] = normalize_spend_date(data["spend_date"])
    journal = Journal(**data)
    session.add(journal)
    session.commit()
    session.refresh(journal)
    return journal


def update_journal(session: Session, journal_id: int, payload: JournalUpdate) -> Journal:
    journal = session.get(Journal, journal_id)
    if journal is None:
        raise HTTPException(status_code=404, detail=f"Journal not found: {journal_id}")
    updates = payload.model_dump(exclude_unset=True)
    if "spend_date" in updates and updates["spend_date"] is not None:
        updates["spend_date"] = normalize_spend_date(updates["spend_date"])
    for field, value in updates.items():
        setattr(journal, field, value)
    session.add(journal)
    session.commit()
    session.refresh(journal)
    return journal


def delete_journal(session: Session, journal_id: int) -> None:
    journal = session.get(Journal, journal_id)
    if journal is None:
        raise HTTPException(status_code=404, detail=f"Journal not found: {journal_id}")
    session.delete(journal)
    session.commit()


def _resolve_settling_account(
    session: Session, spend_way_type: str, spend_way: str
) -> tuple[str, str]:
    """Resolve (account_id, account_name) for a Stock_Detail row.

    Accepts both account-funded and credit-card-funded journals — the latter
    records the credit_card_id/card_name in account_* fields so the holding
    history remains traceable. Caller has already validated the journal payload.
    """
    if spend_way_type == "account":
        # spend_way is the account PK (Account.id); the StockDetail still records
        # the business account_id/name so the holding history stays readable.
        account = _account_by_spend_way(session, spend_way)
        if account is None:
            raise HTTPException(status_code=404, detail=f"Account not found: {spend_way}")
        return account.account_id, account.name
    if spend_way_type == "credit_card":
        card = session.exec(
            select(CreditCard).where(CreditCard.credit_card_id == spend_way)
        ).first()
        if card is None:
            raise HTTPException(status_code=404, detail=f"Credit card not found: {spend_way}")
        return card.credit_card_id, card.card_name
    raise HTTPException(
        status_code=422,
        detail=f"Unsupported spend_way_type for stock transaction: {spend_way_type}",
    )


def _validate_cash_dividend(excute_type: str, spending: float) -> None:
    """A cash dividend is income, so its journal spending must be positive.

    The income statement reads the *signed* journal amount (not ``abs()``), so a
    mis-signed cash dividend would silently shrink 孳息 income while still adding
    to the P&L ``dividends_total`` — reject it up front. Scoped to ``cash`` only:
    buy/sell carry their own load-bearing signs and ``stock`` dividends are 0.
    """
    if excute_type == "cash" and spending <= 0:
        raise HTTPException(
            status_code=422,
            detail="Cash dividend spending must be positive (income inflow).",
        )


def _build_stock_detail(
    journal_row: Journal,
    detail_payload,
    account_id: str,
    account_name: str,
) -> StockDetail:
    return StockDetail(
        stock_id=detail_payload.stock_id,
        excute_type=detail_payload.excute_type,
        excute_amount=detail_payload.excute_amount,
        # Signed pass-through: a buy is negative, a sell is positive — the
        # detail mirrors the journal's cash-flow sign exactly.
        excute_price=journal_row.spending,
        excute_date=detail_payload.excute_date or journal_row.spend_date,
        account_id=account_id,
        account_name=account_name,
        memo=detail_payload.memo if detail_payload.memo is not None else journal_row.note,
    )


def create_journal_with_stock_transaction(
    session: Session, payload: JournalStockTransactionCreate
) -> tuple[Journal, StockDetail]:
    """Insert a Journal row and a Stock_Detail row in a single transaction.

    ``excute_price`` is copied verbatim from ``journal.spending`` — the sign is
    load-bearing (buy/outflow stays negative, sell/inflow stays positive). The
    settling source is looked up from ``journal.spend_way`` (account or credit
    card) so the two rows can never disagree on which payment method funded
    the trade.

    Either both rows persist or neither does: validation errors raise before
    ``session.commit()``, so the surrounding session is rolled back by the
    FastAPI dependency teardown.
    """
    j = payload.journal
    d = payload.stock_detail

    account_id, account_name = _resolve_settling_account(session, j.spend_way_type, j.spend_way)

    holding = session.get(StockJournal, d.stock_id)
    if holding is None:
        raise HTTPException(status_code=404, detail=f"Stock not found: {d.stock_id}")

    _validate_cash_dividend(d.excute_type, j.spending)

    journal_data = j.model_dump()
    journal_data["spend_date"] = normalize_spend_date(journal_data["spend_date"])
    journal_row = Journal(**journal_data)
    session.add(journal_row)
    session.flush()  # assigns distinct_number without committing

    detail = _build_stock_detail(journal_row, d, account_id, account_name)
    session.add(detail)
    session.commit()
    session.refresh(journal_row)
    session.refresh(detail)
    return journal_row, detail


def update_journal_with_stock_transaction(
    session: Session,
    journal_id: int,
    payload: JournalStockTransactionUpdate,
) -> tuple[Journal, StockDetail]:
    """Update an existing Journal and insert a new Stock_Detail atomically.

    Used when a user edits a journal whose original ``action_sub`` was empty
    and now points to a syncable asset (e.g. Stock). The detail row is always
    created fresh — partial updates of existing details should go through the
    independent Stock_Detail endpoints. Either both writes commit or neither.
    """
    j = payload.journal
    d = payload.stock_detail

    journal_row = session.get(Journal, journal_id)
    if journal_row is None:
        raise HTTPException(status_code=404, detail=f"Journal not found: {journal_id}")

    updates = j.model_dump(exclude_unset=True)
    if "spend_date" in updates and updates["spend_date"] is not None:
        updates["spend_date"] = normalize_spend_date(updates["spend_date"])
    for field, value in updates.items():
        setattr(journal_row, field, value)

    account_id, account_name = _resolve_settling_account(
        session, journal_row.spend_way_type, journal_row.spend_way
    )

    holding = session.get(StockJournal, d.stock_id)
    if holding is None:
        raise HTTPException(status_code=404, detail=f"Stock not found: {d.stock_id}")

    # journal_row.spending already reflects the applied update (the payload's
    # spending may be unset, in which case the existing value stands).
    _validate_cash_dividend(d.excute_type, journal_row.spending)

    session.add(journal_row)
    session.flush()

    detail = _build_stock_detail(journal_row, d, account_id, account_name)
    session.add(detail)
    session.commit()
    session.refresh(journal_row)
    session.refresh(detail)
    return journal_row, detail


# ---------- Insurance composite ----------
#
# Divergence from the Stock variants above: Insurance_Journal has no account
# columns, so there is no settling source to resolve from journal.spend_way
# (``_resolve_settling_account`` is deliberately *not* called — funding the
# premium from any spend_way_type is allowed and nothing is stored about it).
# ``excute_price`` is the signed pass-through field, copied verbatim from
# journal.spending.


def _build_insurance_detail(journal_row: Journal, detail_payload) -> InsuranceJournal:
    return InsuranceJournal(
        insurance_id=detail_payload.insurance_id,
        insurance_excute_type=detail_payload.insurance_excute_type,
        # Signed pass-through: a premium/outflow stays negative, a refund/inflow
        # stays positive — the detail mirrors the journal's cash-flow sign.
        excute_price=journal_row.spending,
        excute_date=detail_payload.excute_date or journal_row.spend_date,
        memo=detail_payload.memo if detail_payload.memo is not None else journal_row.note,
    )


def create_journal_with_insurance_transaction(
    session: Session, payload: JournalInsuranceTransactionCreate
) -> tuple[Journal, InsuranceJournal]:
    """Insert a Journal row and an Insurance_Journal row in a single transaction.

    ``excute_price`` is copied verbatim from ``journal.spending`` (sign
    preserved). Unlike the Stock composite there is no settling-account lookup:
    Insurance_Journal records no payment source. Either both rows persist or
    neither does — validation errors raise before ``session.commit()``.
    """
    j = payload.journal
    d = payload.insurance_detail

    policy = session.get(Insurance, d.insurance_id)
    if policy is None:
        raise HTTPException(status_code=404, detail=f"Insurance not found: {d.insurance_id}")

    journal_data = j.model_dump()
    journal_data["spend_date"] = normalize_spend_date(journal_data["spend_date"])
    journal_row = Journal(**journal_data)
    session.add(journal_row)
    session.flush()  # assigns distinct_number without committing

    detail = _build_insurance_detail(journal_row, d)
    session.add(detail)
    session.commit()
    session.refresh(journal_row)
    session.refresh(detail)
    return journal_row, detail


def update_journal_with_insurance_transaction(
    session: Session,
    journal_id: int,
    payload: JournalInsuranceTransactionUpdate,
) -> tuple[Journal, InsuranceJournal]:
    """Update an existing Journal and insert a new Insurance_Journal atomically.

    Used when a user edits a journal whose original ``action_sub`` was empty and
    now points to an insurance policy. The detail row is always created fresh —
    partial updates of existing details go through the independent
    Insurance_Journal endpoints. Either both writes commit or neither.
    """
    j = payload.journal
    d = payload.insurance_detail

    journal_row = session.get(Journal, journal_id)
    if journal_row is None:
        raise HTTPException(status_code=404, detail=f"Journal not found: {journal_id}")

    updates = j.model_dump(exclude_unset=True)
    if "spend_date" in updates and updates["spend_date"] is not None:
        updates["spend_date"] = normalize_spend_date(updates["spend_date"])
    for field, value in updates.items():
        setattr(journal_row, field, value)

    policy = session.get(Insurance, d.insurance_id)
    if policy is None:
        raise HTTPException(status_code=404, detail=f"Insurance not found: {d.insurance_id}")

    session.add(journal_row)
    session.flush()

    detail = _build_insurance_detail(journal_row, d)
    session.add(detail)
    session.commit()
    session.refresh(journal_row)
    session.refresh(detail)
    return journal_row, detail


# ---------- Estate composite ----------
#
# Same shape and divergences as the Insurance composite above: no settling
# source on Estate_Journal, signed pass-through into ``excute_price``.


def _build_estate_detail(journal_row: Journal, detail_payload) -> EstateJournal:
    return EstateJournal(
        estate_id=detail_payload.estate_id,
        estate_excute_type=detail_payload.estate_excute_type,
        # Signed pass-through: a tax/fee/outflow stays negative, a rent/inflow
        # stays positive — the detail mirrors the journal's cash-flow sign.
        excute_price=journal_row.spending,
        excute_date=detail_payload.excute_date or journal_row.spend_date,
        memo=detail_payload.memo if detail_payload.memo is not None else journal_row.note,
    )


def create_journal_with_estate_transaction(
    session: Session, payload: JournalEstateTransactionCreate
) -> tuple[Journal, EstateJournal]:
    """Insert a Journal row and an Estate_Journal row in a single transaction.

    ``excute_price`` is copied verbatim from ``journal.spending`` (sign
    preserved). Unlike the Stock composite there is no settling-account lookup:
    Estate_Journal records no payment source. Either both rows persist or
    neither does — validation errors raise before ``session.commit()``.
    """
    j = payload.journal
    d = payload.estate_detail

    estate = session.get(Estate, d.estate_id)
    if estate is None:
        raise HTTPException(status_code=404, detail=f"Estate not found: {d.estate_id}")

    journal_data = j.model_dump()
    journal_data["spend_date"] = normalize_spend_date(journal_data["spend_date"])
    journal_row = Journal(**journal_data)
    session.add(journal_row)
    session.flush()  # assigns distinct_number without committing

    detail = _build_estate_detail(journal_row, d)
    session.add(detail)
    session.commit()
    session.refresh(journal_row)
    session.refresh(detail)
    return journal_row, detail


def update_journal_with_estate_transaction(
    session: Session,
    journal_id: int,
    payload: JournalEstateTransactionUpdate,
) -> tuple[Journal, EstateJournal]:
    """Update an existing Journal and insert a new Estate_Journal atomically.

    Used when a user edits a journal whose original ``action_sub`` was empty and
    now points to an estate. The detail row is always created fresh — partial
    updates of existing details go through the independent Estate_Journal
    endpoints. Either both writes commit or neither.
    """
    j = payload.journal
    d = payload.estate_detail

    journal_row = session.get(Journal, journal_id)
    if journal_row is None:
        raise HTTPException(status_code=404, detail=f"Journal not found: {journal_id}")

    updates = j.model_dump(exclude_unset=True)
    if "spend_date" in updates and updates["spend_date"] is not None:
        updates["spend_date"] = normalize_spend_date(updates["spend_date"])
    for field, value in updates.items():
        setattr(journal_row, field, value)

    estate = session.get(Estate, d.estate_id)
    if estate is None:
        raise HTTPException(status_code=404, detail=f"Estate not found: {d.estate_id}")

    session.add(journal_row)
    session.flush()

    detail = _build_estate_detail(journal_row, d)
    session.add(detail)
    session.commit()
    session.refresh(journal_row)
    session.refresh(detail)
    return journal_row, detail


# ---------- Loan composite ----------
#
# Two divergences from the Stock/Insurance/Estate composites:
#   * A single repayment splits into a principal portion and an interest portion,
#     each written as its own Loan_Journal row.
#   * Each row stores a POSITIVE magnitude (NOT a signed copy of journal.spending)
#     — the canonical convention every loan reader expects (settlement balance,
#     repayed, cash flow, income statement). journal.spending is the signed total
#     outflow ``−(principal+interest)``; the two are validated to agree.
# Loan_Journal has no account columns, so (like Insurance/Estate) there is no
# settling-source lookup.


def _validate_loan_repayment(spending: float, principal: float, interest: float) -> None:
    """A repayment's principal+interest (positive magnitudes) must match |spending|.

    Either portion may be 0 (interest-only or principal-only) but not both. The
    journal's signed ``spending`` is the total outflow, so its magnitude must
    equal ``principal + interest`` — otherwise the ledger and Loan_Journal would
    disagree on how much was paid.
    """
    if principal < 0 or interest < 0:
        raise HTTPException(
            status_code=422, detail="Loan principal/interest must be non-negative."
        )
    total = round(principal + interest, 2)
    if total <= 0:
        raise HTTPException(
            status_code=422,
            detail="Loan repayment must have a positive principal+interest total.",
        )
    if round(abs(spending), 2) != total:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Journal spending magnitude ({round(abs(spending), 2)}) must equal "
                f"principal + interest ({total})."
            ),
        )


def _build_loan_details(journal_row: Journal, detail_payload) -> list[LoanJournal]:
    """One Loan_Journal row per non-zero portion, each a positive magnitude."""
    excute_date = detail_payload.excute_date or journal_row.spend_date
    memo = detail_payload.memo if detail_payload.memo is not None else journal_row.note
    rows: list[LoanJournal] = []
    if detail_payload.principal > 0:
        rows.append(
            LoanJournal(
                loan_id=detail_payload.loan_id,
                loan_excute_type="principal",
                excute_price=detail_payload.principal,
                excute_date=excute_date,
                memo=memo,
            )
        )
    if detail_payload.interest > 0:
        rows.append(
            LoanJournal(
                loan_id=detail_payload.loan_id,
                loan_excute_type="interest",
                excute_price=detail_payload.interest,
                excute_date=excute_date,
                memo=memo,
            )
        )
    return rows


def create_journal_with_loan_transaction(
    session: Session, payload: JournalLoanTransactionCreate
) -> tuple[Journal, list[LoanJournal]]:
    """Insert a Journal row and its Loan_Journal principal/interest rows atomically.

    The principal/interest split is stored verbatim as positive magnitudes; the
    journal carries the signed total outflow. ``Loan.repayed`` is recomputed from
    all principal rows afterwards. Either everything persists or nothing does.
    """
    from app.services.asset_service import _recalculate_repayed

    j = payload.journal
    d = payload.loan_detail

    loan = session.get(Loan, d.loan_id)
    if loan is None:
        raise HTTPException(status_code=404, detail=f"Loan not found: {d.loan_id}")

    _validate_loan_repayment(j.spending, d.principal, d.interest)

    journal_data = j.model_dump()
    journal_data["spend_date"] = normalize_spend_date(journal_data["spend_date"])
    journal_row = Journal(**journal_data)
    session.add(journal_row)
    session.flush()  # assigns distinct_number without committing

    details = _build_loan_details(journal_row, d)
    for row in details:
        session.add(row)
    session.commit()
    session.refresh(journal_row)
    for row in details:
        session.refresh(row)
    _recalculate_repayed(session, d.loan_id)
    return journal_row, details


def update_journal_with_loan_transaction(
    session: Session,
    journal_id: int,
    payload: JournalLoanTransactionUpdate,
) -> tuple[Journal, list[LoanJournal]]:
    """Update an existing Journal and insert fresh Loan_Journal rows atomically.

    Used when re-classifying a previously-untagged journal as a loan repayment.
    The detail rows are always created fresh — partial edits of existing rows go
    through the independent Loan_Journal endpoints. Either both writes commit or
    neither.
    """
    from app.services.asset_service import _recalculate_repayed

    j = payload.journal
    d = payload.loan_detail

    journal_row = session.get(Journal, journal_id)
    if journal_row is None:
        raise HTTPException(status_code=404, detail=f"Journal not found: {journal_id}")

    updates = j.model_dump(exclude_unset=True)
    if "spend_date" in updates and updates["spend_date"] is not None:
        updates["spend_date"] = normalize_spend_date(updates["spend_date"])
    for field, value in updates.items():
        setattr(journal_row, field, value)

    loan = session.get(Loan, d.loan_id)
    if loan is None:
        raise HTTPException(status_code=404, detail=f"Loan not found: {d.loan_id}")

    # journal_row.spending reflects the applied update (an unset spending keeps
    # the existing value).
    _validate_loan_repayment(journal_row.spending, d.principal, d.interest)

    session.add(journal_row)
    session.flush()

    details = _build_loan_details(journal_row, d)
    for row in details:
        session.add(row)
    session.commit()
    session.refresh(journal_row)
    for row in details:
        session.refresh(row)
    _recalculate_repayed(session, d.loan_id)
    return journal_row, details


# ---------- Analytics ----------


def compute_expenditure_ratio(session: Session, vesting_month: str) -> ExpenditureRatioResponse:
    """Outer pie grouped by action_main_type, inner by action_sub_type.

    Each category (action_main) and sub (action_sub) is netted then floored at 0
    by side — income via ``floor_income``, everything else as an outflow via
    ``floor_expense`` — so a mis-typed inflow or a reimbursed 代買 can't inflate
    (or, via the old ``abs()``, flip) a slice. Invest/transfer rows are excluded.
    """
    journals = list_journals_by_month(session, vesting_month)
    excluded = INVEST_MAIN_TYPES | TRANSFER_MAIN_TYPES | FINANCING_MAIN_TYPES
    main_net: dict[str, float] = defaultdict(float)
    main_type: dict[str, str] = {}
    sub_net: dict[str, float] = defaultdict(float)
    sub_is_income: dict[str, bool] = {}
    for j in journals:
        if norm_type(j.action_main_type) in excluded:
            continue
        is_income = norm_type(j.action_main_type) in INCOME_MAIN_TYPES
        main_net[j.action_main] += j.spending
        main_type.setdefault(j.action_main, j.action_main_type)
        # The inner pie groups by action_sub_type and floors by the *main*
        # category's side (a sub label like "salary" is not itself an income
        # type, but its income parent makes its net inflow legitimate).
        if j.action_sub_type:
            sub_net[j.action_sub_type] += j.spending
            sub_is_income.setdefault(j.action_sub_type, is_income)

    def floored(is_income: bool, net: float) -> float:
        return floor_income(net) if is_income else floor_expense(net)

    outer: dict[str, float] = defaultdict(float)
    for cat, value in main_net.items():
        amount = floored(norm_type(main_type[cat]) in INCOME_MAIN_TYPES, value)
        if amount > 0.005:
            outer[main_type[cat]] += amount
    inner: dict[str, float] = defaultdict(float)
    for stype, value in sub_net.items():
        amount = floored(sub_is_income[stype], value)
        if amount > 0.005:
            inner[stype] += amount

    # Loan repayment slice (財務行為) — the loanrepayment Journal is excluded above
    # (FINANCING), so we add it back from Loan_Journal purely to make the cash
    # outflow visible / proportional in the pie. Outer = LoanRepayment, inner =
    # principal / interest. No double-count (same source as cash flow).
    loan = loan_repayment_by_bucket(session, vesting_month, vesting_month, lambda _m: vesting_month)
    legs = loan.get(vesting_month, {})
    principal = legs.get("principal", 0.0)
    interest = legs.get("interest", 0.0)
    if principal + interest > 0.005:
        outer["LoanRepayment"] += principal + interest
    if principal > 0.005:
        inner["principal"] += principal
    if interest > 0.005:
        inner["interest"] += interest

    return ExpenditureRatioResponse(
        outer=[ExpenditureRatioItem(name=k, value=round(v, 2)) for k, v in outer.items()],
        inner=[ExpenditureRatioItem(name=k, value=round(v, 2)) for k, v in inner.items()],
    )


def compute_uncategorized_summary(session: Session) -> UncategorizedSummaryResponse:
    """Count journals whose action_main_type falls outside every report bucket.

    Legacy e-invoice imports left thousands of rows typed 'undefined'/'No'/'' —
    invisible to the type-bucketed reports until the user classifies them. The
    summary powers the dashboard cleanup card and the ledger banner: total
    across all months plus a per-month breakdown (newest first, zero months
    omitted).
    """
    rows = session.exec(
        select(Journal.vesting_month, Journal.action_main_type)
    ).all()
    per_month: dict[str, int] = defaultdict(int)
    for vesting_month, action_main_type in rows:
        if is_uncategorized(action_main_type):
            per_month[vesting_month] += 1
    months = [
        UncategorizedMonthCount(vesting_month=m, count=per_month[m])
        for m in sorted(per_month, reverse=True)
    ]
    return UncategorizedSummaryResponse(
        total=sum(per_month.values()), months=months
    )


def compute_invest_ratio(session: Session, vesting_month: str) -> InvestRatioResponse:
    journals = list_journals_by_month(session, vesting_month)
    items: dict[str, float] = {}
    for j in journals:
        if norm_type(j.action_main_type) not in INVEST_MAIN_TYPES:
            continue
        key = j.action_sub_type or j.action_main_type
        items[key] = items.get(key, 0.0) + abs(j.spending)
    return InvestRatioResponse(
        items=[InvestRatioItem(name=k, value=round(v, 2)) for k, v in items.items()]
    )


def compute_expenditure_budget(
    session: Session, vesting_month: str
) -> ExpenditureBudgetResponse:
    year = vesting_month[:4]
    mm = vesting_month[-2:]
    budget_field = f"expected{mm}"

    event_codes = {
        c.code_id for c in session.exec(select(CodeData)).all() if c.is_annual_event
    }

    # Group by a normalized type key so a budget ``code_type`` ("fixed") and a
    # journal ``action_main_type`` ("Fixed") that differ only in casing align in
    # the same row instead of splitting expected/actual apart. ``label_by_type``
    # keeps the original casing for display (budget's preferred, journal's as a
    # fallback for types that only appear in journals, e.g. invest/transfer).
    budget_rows = list(session.exec(select(Budget).where(Budget.budget_year == year)).all())
    expected_by_type: dict[str, float] = {}
    label_by_type: dict[str, str] = {}
    for b in budget_rows:
        if b.category_code in event_codes:
            continue
        amt = float(getattr(b, budget_field) or 0.0)
        key = norm_type(b.code_type)
        expected_by_type[key] = expected_by_type.get(key, 0.0) + amt
        label_by_type.setdefault(key, b.code_type or key)

    journals = list_journals_by_month(session, vesting_month)
    # Net per category first, then floor at 0 by side, then roll up to type — so a
    # mis-typed inflow or a reimbursed 代買 cannot inflate a type's actual.
    cat_net: dict[str, float] = defaultdict(float)
    cat_type: dict[str, str] = {}
    for j in journals:
        if j.action_main in event_codes:
            continue
        # Loan repayments are report-neutral (sourced from Loan_Journal); never
        # count them as a budget actual — that would double-count vs the cash
        # flow / income statement.
        if norm_type(j.action_main_type) in FINANCING_MAIN_TYPES:
            continue
        cat_net[j.action_main] += j.spending
        cat_type.setdefault(j.action_main, j.action_main_type)
    actual_by_type: dict[str, float] = defaultdict(float)
    for cat, value in cat_net.items():
        raw_type = cat_type[cat]
        key = norm_type(raw_type)
        amount = floor_income(value) if key in INCOME_MAIN_TYPES else floor_expense(value)
        actual_by_type[key] += amount
        label_by_type.setdefault(key, raw_type or key)

    rows: list[ExpenditureBudgetRow] = []
    for action_type in sorted(set(expected_by_type) | set(actual_by_type)):
        expected = round(expected_by_type.get(action_type, 0.0), 2)
        actual = round(actual_by_type.get(action_type, 0.0), 2)
        diff = round(actual - expected, 2)
        usage = round(actual / expected, 4) if expected else 0.0
        rows.append(
            ExpenditureBudgetRow(
                action_main_type=label_by_type.get(action_type, action_type),
                expected=expected,
                actual=actual,
                diff=diff,
                usage_rate=usage,
            )
        )
    return ExpenditureBudgetResponse(rows=rows)


def compute_liability(session: Session, vesting_month: str) -> LiabilityResponse:
    journals = list_journals_by_month(session, vesting_month)
    by_card: dict[str, float] = {}
    for j in journals:
        if j.spend_way_type != "credit_card":
            continue
        by_card[j.spend_way] = by_card.get(j.spend_way, 0.0) + abs(j.spending)

    items: list[LiabilityItem] = []
    for card_id, amount in by_card.items():
        card = session.exec(
            select(CreditCard).where(CreditCard.credit_card_id == card_id)
        ).first()
        items.append(
            LiabilityItem(
                credit_card_id=card_id,
                credit_card_name=card.card_name if card is not None else card_id,
                amount=round(amount, 2),
            )
        )
    return LiabilityResponse(items=items)
