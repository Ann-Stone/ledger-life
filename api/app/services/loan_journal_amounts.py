"""Shared loan-repayment amount helpers (low-level, cross-domain).

``Loan_Journal`` stores every repayment leg as a **positive magnitude**
(``excute_price``) tagged by ``loan_excute_type`` — ``principal`` / ``interest``
/ ``fee`` (servicing) and ``increment`` (new borrowing). The 損益表 and
現金流量表 already read this table directly; this module factors out the two
pieces both the reports domain *and* the monthly domain need, so neither has to
import the other (the monthly domain must not depend on the reports domain — see
``journal_types`` module doc).

The ``loanrepayment`` main Journal row is report-neutral (excluded from every
type-bucketed report), so summing repayment legs from ``Loan_Journal`` here never
double-counts: it is the *same* source the cash-flow / income-statement use.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

from sqlmodel import Session, select

from app.models.assets.loan import Loan, LoanJournal
from app.models.settings.account import Account
from app.services.fx_lookup import BASE_CURRENCY, fx_rate_for_month


def loanjournal_amount_twd(
    session: Session,
    row: LoanJournal,
    loan_by_id: dict[str, Loan],
    fx_cache: dict[tuple[str, str], float],
) -> float:
    """``LoanJournal.excute_price`` (a positive magnitude) converted to TWD.

    Currency follows the loan's repayment account (``Loan.account_id`` →
    ``Account.fx_code``); the rate is taken for the excute_date's month. Domestic
    loans stay 1:1.
    """
    loan = loan_by_id.get(row.loan_id)
    fx_code = BASE_CURRENCY
    if loan is not None:
        account = session.exec(
            select(Account).where(Account.account_id == loan.account_id)
        ).first()
        if account is not None and account.fx_code:
            fx_code = account.fx_code
    month = (row.excute_date or "")[:6]
    if fx_code == BASE_CURRENCY or len(month) != 6:
        return row.excute_price
    key = (fx_code, month)
    if key not in fx_cache:
        fx_cache[key] = fx_rate_for_month(session, fx_code, month)
    return row.excute_price * fx_cache[key]


def loan_repayment_by_bucket(
    session: Session,
    start_vm: str,
    end_vm: str,
    bucket_of: Callable[[str], str],
) -> dict[str, dict[str, float]]:
    """Repayment outflow (TWD) per period bucket, split principal vs interest.

    Scans ``Loan_Journal`` rows whose ``excute_date`` month falls in
    ``[start_vm, end_vm]`` (inclusive, ``YYYYMM`` string compare). ``bucket_of``
    maps a ``YYYYMM`` month to its period key (a month, a year, or a constant for
    a single whole-window bucket). Returns
    ``{bucket: {"principal": float, "interest": float}}`` where ``interest`` folds
    in ``fee``. ``increment`` (new borrowing — a cash *inflow*, not spending) is
    intentionally excluded.
    """
    loan_by_id = {loan.loan_id: loan for loan in session.exec(select(Loan)).all()}
    fx_cache: dict[tuple[str, str], float] = {}
    out: dict[str, dict[str, float]] = defaultdict(
        lambda: {"principal": 0.0, "interest": 0.0}
    )
    for lr in session.exec(select(LoanJournal)).all():
        month = (lr.excute_date or "")[:6]
        if len(month) != 6 or not (start_vm <= month <= end_vm):
            continue
        et = (lr.loan_excute_type or "").strip().lower()
        if et == "principal":
            out[bucket_of(month)]["principal"] += loanjournal_amount_twd(
                session, lr, loan_by_id, fx_cache
            )
        elif et in {"interest", "fee"}:
            out[bucket_of(month)]["interest"] += loanjournal_amount_twd(
                session, lr, loan_by_id, fx_cache
            )
    return dict(out)
