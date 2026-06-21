"""Retirement-readiness service — Dashboard domain.

Sizes a perpetual FIRE target from recurring *consumption* (loan repayment
excluded — finite + principal is saving) and compares it to current net worth
(which already nets the loan as a liability). Separately reports the during-loan
cash-flow picture: debt-service-to-income and per-loan payoff projection.

Nothing here writes to the ledger or mutates any report; it is a read-only
overlay plus a tiny single-row settings table.
"""
from __future__ import annotations

import math
from datetime import datetime

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.assets.loan import Loan, LoanJournal
from app.models.dashboard.retirement import (
    LoanPayoff,
    RetirementReadinessRead,
    RetirementSetting,
    RetirementSettingUpdate,
)
from app.models.monthly_report.estate_net_value_history import EstateNetValueHistory
from app.models.monthly_report.journal import Journal
from app.models.settings.account import Account
from app.services.expense_netting import (
    category_net_by_bucket,
    floor_expense,
    floor_income,
)
from app.services.fx_lookup import BASE_CURRENCY, fx_rate_for_month
from app.services.journal_types import (
    EXPENSE_MAIN_TYPES,
    INCOME_MAIN_TYPES,
    norm_type,
)
from app.services.loan_journal_amounts import (
    loan_repayment_by_bucket,
    loanjournal_amount_twd,
)
from app.services.month_utils import shift_month
from app.services.report_service import (
    _latest_per_entity,
    get_balance_sheet,
    journal_amount_twd,
)

_SETTINGS_ROW_ID = 1
_DEFAULT_WITHDRAWAL_RATE = 0.04
# EstateNetValueHistory.estate_status value meaning "owner lives in it" (自住).
_SELF_OCCUPIED_STATUS = "live"


def _current_month() -> str:
    return datetime.now().strftime("%Y%m")


# ---------- Settings (single row) ----------


def get_retirement_settings(session: Session) -> RetirementSetting:
    """The persisted config, or in-memory defaults when never set."""
    row = session.get(RetirementSetting, _SETTINGS_ROW_ID)
    return row if row is not None else RetirementSetting()


def update_retirement_settings(
    session: Session, payload: RetirementSettingUpdate
) -> RetirementSetting:
    """Upsert the single config row. ``withdrawal_rate=None`` keeps the current
    rate; ``annual_expense_override`` is set verbatim (``null`` clears it)."""
    row = session.get(RetirementSetting, _SETTINGS_ROW_ID)
    if row is None:
        row = RetirementSetting(id=_SETTINGS_ROW_ID)
    if payload.withdrawal_rate is not None:
        if not (0.001 <= payload.withdrawal_rate <= 0.5):
            raise HTTPException(
                status_code=422, detail="withdrawal_rate must be between 0.001 and 0.5"
            )
        row.withdrawal_rate = payload.withdrawal_rate
    # Full-replace semantics for the override: the settings form always sends the
    # intended value, so null here means "no override".
    override = payload.annual_expense_override
    row.annual_expense_override = override if (override and override > 0) else None
    if payload.exclude_self_occupied_estate is not None:
        row.exclude_self_occupied_estate = payload.exclude_self_occupied_estate
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


# ---------- Readiness ----------


def _loan_fx_code(session: Session, loan: Loan) -> str:
    account = session.exec(
        select(Account).where(Account.account_id == loan.account_id)
    ).first()
    if account is not None and account.fx_code:
        return account.fx_code
    return BASE_CURRENCY


def _loan_payoffs(session: Session, anchor: str) -> list[LoanPayoff]:
    """Per-loan remaining balance (TWD) + projected payoff from recent velocity.

    Payoff months are estimated empirically: average monthly principal over the
    trailing 12 months (in the loan's native units, matching the native
    remaining balance) → remaining ÷ that rate. ``monthly_payment`` is the recent
    average principal+interest, TWD.
    """
    start = shift_month(anchor, -11)
    loans = list(session.exec(select(Loan).order_by(Loan.loan_index)).all())
    loan_by_id = {loan.loan_id: loan for loan in loans}
    fx_cache: dict[tuple[str, str], float] = {}
    out: list[LoanPayoff] = []
    for loan in loans:
        remaining_native = max(loan.amount - loan.repayed, 0.0)
        fx_code = _loan_fx_code(session, loan)
        rate = 1.0 if fx_code == BASE_CURRENCY else fx_rate_for_month(session, fx_code, anchor)
        remaining_twd = round(remaining_native * rate, 2)

        rows = session.exec(
            select(LoanJournal).where(LoanJournal.loan_id == loan.loan_id)
        ).all()
        principal_native = 0.0
        payment_twd = 0.0
        active_months: set[str] = set()
        for lr in rows:
            month = (lr.excute_date or "")[:6]
            if len(month) != 6 or not (start <= month <= anchor):
                continue
            et = (lr.loan_excute_type or "").strip().lower()
            if et == "increment":
                continue  # new borrowing is not a payment
            active_months.add(month)
            twd = loanjournal_amount_twd(session, lr, loan_by_id, fx_cache)
            payment_twd += twd
            if et == "principal":
                principal_native += lr.excute_price

        n_months = len(active_months)
        monthly_payment = round(payment_twd / n_months, 2) if n_months else 0.0

        payoff_month: str | None = None
        years_left: float | None = None
        if remaining_native <= 0.005:
            years_left = 0.0
        elif n_months and principal_native > 0:
            avg_principal = principal_native / n_months
            remaining_months = math.ceil(remaining_native / avg_principal)
            payoff_month = shift_month(anchor, remaining_months)
            years_left = round(remaining_months / 12, 1)

        out.append(
            LoanPayoff(
                loan_id=loan.loan_id,
                loan_name=loan.loan_name,
                remaining_balance=remaining_twd,
                monthly_payment=monthly_payment,
                payoff_month=payoff_month,
                years_left=years_left,
            )
        )
    return out


def _self_occupied_estate_twd(session: Session) -> float:
    """Latest-snapshot market value (TWD) of self-occupied real estate.

    Sums ``market_value * fx_rate`` over the latest ``EstateNetValueHistory`` row
    per estate whose ``estate_status`` is self-occupied (``'live'``). Mirrors how
    ``get_balance_sheet`` values estates (same ``_latest_per_entity`` de-dup), so
    the result is exactly the estate contribution to balance-sheet net worth.
    Returns ``0.0`` when no estate is marked self-occupied.
    """
    rows = list(session.exec(select(EstateNetValueHistory)).all())
    total = sum(
        round(r.market_value * r.fx_rate, 2)
        for r in _latest_per_entity(rows, key=lambda r: r.id)
        if (r.estate_status or "").strip().lower() == _SELF_OCCUPIED_STATUS
    )
    return round(total, 2)


def get_retirement_readiness(
    session: Session, as_of: str | None = None
) -> RetirementReadinessRead:
    """Point-in-time readiness on the consumption basis + debt-service health.

    ``as_of`` (``YYYYMM``) anchors the trailing-12-month window; defaults to the
    current month. Net worth is the latest balance-sheet value (already nets the
    loan), so it is independent of the anchor.
    """
    anchor = as_of or _current_month()
    start = shift_month(anchor, -11)
    settings = get_retirement_settings(session)

    net_worth = get_balance_sheet(session).net_worth
    # A home you live in cannot fund retirement, so optionally net it out of the
    # readiness net worth. Identified by estate_status 'live'; nothing marked
    # self-occupied → 0 excluded.
    self_occupied_value = (
        _self_occupied_estate_twd(session)
        if settings.exclude_self_occupied_estate
        else 0.0
    )
    net_worth = round(net_worth - self_occupied_value, 2)

    journals = list(
        session.exec(
            select(Journal)
            .where(Journal.vesting_month >= start)
            .where(Journal.vesting_month <= anchor)
        ).all()
    )
    fx_cache: dict[tuple[str, str], float] = {}
    net, cat_type = category_net_by_bucket(
        journals,
        bucket_of=lambda _j: "all",
        amount_of=lambda j: journal_amount_twd(session, j, fx_cache),
    )
    income_12m = 0.0
    consumption_12m = 0.0  # fixed + floating, loan repayment excluded
    for (_bucket, cat), value in net.items():
        t = norm_type(cat_type[cat])
        if t in INCOME_MAIN_TYPES:
            income_12m += floor_income(value)
        elif t in EXPENSE_MAIN_TYPES:
            consumption_12m += floor_expense(value)

    if settings.annual_expense_override and settings.annual_expense_override > 0:
        annual_expense_base = round(settings.annual_expense_override, 2)
        expense_base_source = "override"
    else:
        annual_expense_base = round(consumption_12m, 2)
        expense_base_source = "computed"

    rate = settings.withdrawal_rate or _DEFAULT_WITHDRAWAL_RATE
    target_portfolio = round(annual_expense_base / rate, 2) if rate > 0 else 0.0
    readiness_pct = round(net_worth / target_portfolio, 4) if target_portfolio > 0 else 0.0
    gap = round(target_portfolio - net_worth, 2)

    loan_legs = loan_repayment_by_bucket(session, start, anchor, lambda _m: "all").get(
        "all", {}
    )
    loan_payment_12m = loan_legs.get("principal", 0.0) + loan_legs.get("interest", 0.0)
    monthly_income = round(income_12m / 12, 2)
    monthly_loan_payment = round(loan_payment_12m / 12, 2)
    debt_service_ratio = (
        round(loan_payment_12m / income_12m, 4) if income_12m > 0 else 0.0
    )

    return RetirementReadinessRead(
        net_worth=net_worth,
        exclude_self_occupied_estate=settings.exclude_self_occupied_estate,
        self_occupied_estate_value=self_occupied_value,
        annual_expense_base=annual_expense_base,
        expense_base_source=expense_base_source,
        withdrawal_rate=rate,
        target_portfolio=target_portfolio,
        readiness_pct=readiness_pct,
        gap=gap,
        monthly_income=monthly_income,
        monthly_loan_payment=monthly_loan_payment,
        debt_service_ratio=debt_service_ratio,
        loans=_loan_payoffs(session, anchor),
    )
