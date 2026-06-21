"""Reports domain service functions (BE-025).

Aggregates Phase 1 monthly snapshots into balance sheet, expenditure trend,
and asset composition views. FX-converts everything to ``BASE_CURRENCY``.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from typing import Literal

from sqlmodel import Session, select

from app.models.assets.loan import Loan, LoanJournal
from app.models.assets.other_asset import OtherAsset
from app.models.assets.stock import StockJournal
from app.models.assets.stock_category import StockCategory
from app.models.monthly_report.account_balance import AccountBalance
from app.models.monthly_report.credit_card_balance import CreditCardBalance
from app.models.monthly_report.estate_net_value_history import EstateNetValueHistory
from app.models.monthly_report.insurance_net_value_history import (
    InsuranceNetValueHistory,
)
from app.models.monthly_report.journal import Journal
from app.models.monthly_report.loan_balance import LoanBalance
from app.models.monthly_report.stock_net_value_history import StockNetValueHistory
from app.models.reports.asset_breakdown import AssetBreakdownRead, AssetShare
from app.models.reports.stock_allocation import StockAllocationRead, StockAllocationShare
from app.models.reports.balance import (
    BalanceAssets,
    BalanceLiabilities,
    BalanceLine,
    BalanceSheetRead,
)
from app.models.reports.budget_variance import (
    BudgetVarianceRead,
    BudgetVarianceRow,
    BudgetVarianceSummary,
)
from app.models.reports.cash_flow import (
    CashFlowActivity,
    CashFlowItem,
    CashFlowPoint,
    CashFlowRead,
    CashFlowSummary,
)
from app.models.reports.expense_insights import (
    ExpenseInsightsRead,
    LargeTxn,
    YoYRow,
)
from app.models.reports.expenditure import ExpenditurePoint, ExpenditureTrendRead
from app.models.reports.expenditure_composition import (
    ExpenditureCategoryNode,
    ExpenditureCompositionRead,
    ExpenditureSubNode,
)
from app.models.reports.income_expense import (
    IncomeExpensePoint,
    IncomeExpenseReportRead,
    IncomeExpenseSummary,
)
from app.models.reports.income_statement import (
    IncomeStatementPoint,
    IncomeStatementReportRead,
    IncomeStatementSummary,
)
from app.models.settings.account import Account
from app.models.settings.budget import Budget
from app.models.settings.code_data import CodeData
from app.models.settings.credit_card import CreditCard
from app.services.expense_netting import (
    category_net_by_bucket,
    floor_expense,
    floor_income,
)
from app.services.fx_lookup import BASE_CURRENCY, fx_rate_for_month
from app.services.journal_types import (
    ACTIVE_INCOME_TYPES,
    EXPENSE_MAIN_TYPES,
    INCOME_MAIN_TYPES,
    INVEST_MAIN_TYPES,
    PASSIVE_INCOME_TYPES,
    REALIZED_GAIN_NAMES,
    TRANSFER_MAIN_TYPES,
    norm_type,
)
from app.services.loan_journal_amounts import (
    loan_repayment_by_bucket,
    loanjournal_amount_twd as _loanjournal_amount_twd,
)
from app.services.month_utils import shift_month


def _latest_per_entity(rows, key):
    """Pick the row with the largest ``vesting_month`` per entity ``key(row)``."""
    latest: dict[str, object] = {}
    for r in rows:
        k = key(r)
        if k not in latest or r.vesting_month > latest[k].vesting_month:
            latest[k] = r
    return list(latest.values())


def get_balance_sheet(session: Session) -> BalanceSheetRead:
    accounts_rows = list(session.exec(select(AccountBalance)).all())
    accounts_latest = _latest_per_entity(accounts_rows, key=lambda r: r.id)
    accounts_lines = [
        BalanceLine(
            name=r.name,
            amount=round(r.balance * r.fx_rate, 2),
            original_amount=round(r.balance, 2),
            currency=r.fx_code,
        )
        for r in accounts_latest
        if r.is_calculate == "Y"
    ]

    stock_rows = list(session.exec(select(StockNetValueHistory)).all())
    stocks_lines = [
        BalanceLine(
            name=r.stock_name,
            amount=round(r.price * r.fx_rate, 2),
            original_amount=round(r.price, 2),
            currency=r.fx_code,
        )
        for r in _latest_per_entity(stock_rows, key=lambda r: r.id)
    ]

    estate_rows = list(session.exec(select(EstateNetValueHistory)).all())
    estates_lines = [
        BalanceLine(
            name=r.name,
            amount=round(r.market_value * r.fx_rate, 2),
            original_amount=round(r.market_value, 2),
            currency=r.fx_code,
        )
        for r in _latest_per_entity(estate_rows, key=lambda r: r.id)
    ]

    insurance_rows = list(session.exec(select(InsuranceNetValueHistory)).all())
    insurance_lines = [
        BalanceLine(
            name=r.name,
            amount=round(r.surrender_value * r.fx_rate, 2),
            original_amount=round(r.surrender_value, 2),
            currency=r.fx_code,
        )
        for r in _latest_per_entity(insurance_rows, key=lambda r: r.id)
    ]

    loan_rows = list(session.exec(select(LoanBalance)).all())
    loan_lines = [
        BalanceLine(
            name=r.name,
            amount=round(r.balance * r.fx_rate, 2),
            original_amount=round(r.balance, 2),
            currency=r.fx_code,
        )
        for r in _latest_per_entity(loan_rows, key=lambda r: r.id)
    ]

    cc_rows = list(session.exec(select(CreditCardBalance)).all())
    cc_lines = [
        BalanceLine(
            name=r.name,
            amount=round(r.balance * r.fx_rate, 2),
            original_amount=round(r.balance, 2),
            currency=BASE_CURRENCY,
        )
        for r in _latest_per_entity(cc_rows, key=lambda r: r.id)
    ]

    asset_total = sum(line.amount for line in accounts_lines + stocks_lines + estates_lines + insurance_lines)
    liability_total = sum(line.amount for line in loan_lines + cc_lines)
    net_worth = round(asset_total + liability_total, 2)  # liabilities are negative

    return BalanceSheetRead(
        assets=BalanceAssets(
            accounts=accounts_lines,
            stocks=stocks_lines,
            estates=estates_lines,
            insurances=insurance_lines,
        ),
        liabilities=BalanceLiabilities(loans=loan_lines, credit_cards=cc_lines),
        net_worth=net_worth,
    )


def _account_fx_code(session: Session, spend_way: str) -> str | None:
    """Resolve an Account's fx_code from Journal.spend_way (stringified Account.id)."""
    try:
        pk = int(spend_way)
    except (TypeError, ValueError):
        return None
    account = session.get(Account, pk)
    return account.fx_code if account is not None else None


def _card_fx_code(session: Session, spend_way: str) -> str | None:
    """Resolve a CreditCard's fx_code from Journal.spend_way (credit_card_id PK)."""
    card = session.get(CreditCard, spend_way)
    return card.fx_code if card is not None else None


def journal_fx_code(session: Session, journal: Journal) -> str:
    """Transaction currency of a journal, inferred from its payment source.

    Falls back to ``BASE_CURRENCY`` for unknown/dangling payment sources so
    callers never crash on legacy rows.
    """
    if journal.spend_way_table == "Account":
        return _account_fx_code(session, journal.spend_way) or BASE_CURRENCY
    if journal.spend_way_table == "Credit_Card":
        return _card_fx_code(session, journal.spend_way) or BASE_CURRENCY
    return BASE_CURRENCY


def journal_amount_twd(
    session: Session,
    journal: Journal,
    fx_cache: dict[tuple[str, str], float] | None = None,
) -> float:
    """Signed ``journal.spending`` converted to base currency (TWD).

    Unlike the monthly ``compute_gain_loss`` (which only converts account-funded
    rows), this also converts credit-card-funded spending via ``CreditCard.fx_code``.
    The sign is preserved verbatim (positive = income, negative = expense) so
    callers can compute net cash flow; take ``abs()`` only for expense-magnitude
    aggregations. Pass a shared ``fx_cache`` keyed by ``(fx_code, vesting_month)``
    when looping to avoid repeated rate lookups.
    """
    fx_code = journal_fx_code(session, journal)
    if fx_code == BASE_CURRENCY:
        return journal.spending
    if fx_cache is None:
        fx_cache = {}
    key = (fx_code, journal.vesting_month)
    if key not in fx_cache:
        fx_cache[key] = fx_rate_for_month(session, fx_code, journal.vesting_month)
    return journal.spending * fx_cache[key]


def list_journals_by_range(
    session: Session, start_vesting_month: str, end_vesting_month: str
) -> list[Journal]:
    """All journals with ``start <= vesting_month <= end`` (inclusive), ordered."""
    statement = (
        select(Journal)
        .where(Journal.vesting_month >= start_vesting_month)
        .where(Journal.vesting_month <= end_vesting_month)
        .order_by(Journal.spend_date.asc(), Journal.distinct_number.asc())
    )
    return list(session.exec(statement).all())


def _period_window(
    type: Literal["monthly", "yearly"], vesting_month: str
) -> tuple[list[str], Callable[[str], str], str, str]:
    """Period axis for a trend: ``(periods oldest-first, bucket_of, start_vm, end_vm)``.

    ``monthly`` → 12 ``YYYYMM`` points ending at ``vesting_month``; ``yearly`` →
    10 ``YYYY`` points ending at that year. ``bucket_of`` maps a journal's
    ``vesting_month`` to its period key; ``start_vm``/``end_vm`` bound the
    inclusive query window. Shared by every range-based report so the windowing
    logic lives in one place.
    """
    if type == "monthly":
        periods = [shift_month(vesting_month, -i) for i in range(11, -1, -1)]
        return periods, (lambda vm: vm), periods[0], periods[-1]
    end_year = int(vesting_month[:4])
    years = [str(y) for y in range(end_year - 9, end_year + 1)]
    return years, (lambda vm: vm[:4]), f"{years[0]}01", f"{years[-1]}12"


def get_expenditure_trend(
    session: Session,
    type: Literal["monthly", "yearly"],
    vesting_month: str,
) -> ExpenditureTrendRead:
    periods, bucket_of, start_vm, end_vm = _period_window(type, vesting_month)
    journals = list_journals_by_range(session, start_vm, end_vm)
    fx_cache: dict[tuple[str, str], float] = {}
    # Net per (period, category) then floor at 0 per category, so a mis-typed
    # inflow or a reimbursed 代買 cannot inflate the period. FX-convert first
    # (raw sums would mix USD card spend with TWD).
    net, cat_type = category_net_by_bucket(
        journals,
        bucket_of=lambda j: bucket_of(j.vesting_month),
        amount_of=lambda j: journal_amount_twd(session, j, fx_cache),
    )
    sums: dict[str, float] = {p: 0.0 for p in periods}
    for (bucket, cat), value in net.items():
        if bucket in sums and norm_type(cat_type[cat]) in EXPENSE_MAIN_TYPES:
            sums[bucket] += floor_expense(value)

    return ExpenditureTrendRead(
        type=type,
        points=[ExpenditurePoint(period=p, amount=round(sums[p], 2)) for p in periods],
    )


def get_income_expense_report(
    session: Session,
    type: Literal["monthly", "yearly"],
    vesting_month: str,
) -> IncomeExpenseReportRead:
    """Income-statement view: per-period income / fixed / floating / net plus an
    annual summary with savings rate.

    Each category's signed cash flow is netted before counting, then floored at 0
    per category (``floor_expense`` / ``floor_income``) — a reimbursed 代買 or a
    mis-typed inflow can neither inflate expense nor cancel another category. The
    per-period **points** floor within each month; the **summary** nets each
    category across the whole window (the "monthly" window is one calendar year,
    so a 代買 reimbursed in a later month still offsets in the annual totals).
    The summary therefore can differ from the sum of the points when an offset
    spans months — it is the netted-over-the-year truth. Invest and transfer rows
    are excluded; ``action_main_type`` is matched case-insensitively (``norm_type``).
    """
    periods, bucket_of, start_vm, end_vm = _period_window(type, vesting_month)
    journals = list_journals_by_range(session, start_vm, end_vm)
    fx_cache: dict[tuple[str, str], float] = {}
    net, cat_type = category_net_by_bucket(
        journals,
        bucket_of=lambda j: bucket_of(j.vesting_month),
        amount_of=lambda j: journal_amount_twd(session, j, fx_cache),
    )

    income = {p: 0.0 for p in periods}
    fixed = {p: 0.0 for p in periods}
    floating = {p: 0.0 for p in periods}
    window_net: dict[str, float] = defaultdict(float)
    for (bucket, cat), value in net.items():
        window_net[cat] += value
        if bucket not in income:
            continue
        t = norm_type(cat_type[cat])
        if t in INCOME_MAIN_TYPES:
            income[bucket] += floor_income(value)
        elif t == "fixed":
            fixed[bucket] += floor_expense(value)
        elif t == "floating":
            floating[bucket] += floor_expense(value)
        # invest / transfer / loanrepayment intentionally excluded

    # Loan repayment (本金+利息) per period — purely additive context for the
    # spending chart; sourced from Loan_Journal (the report-neutral loan Journal
    # stays excluded above, so no double-count). It does NOT enter expense / net /
    # savings_rate, which stay on the consumption basis.
    loan_buckets = loan_repayment_by_bucket(session, start_vm, end_vm, bucket_of)

    points: list[IncomeExpensePoint] = []
    for p in periods:
        inc = round(income[p], 2)
        fx = round(fixed[p], 2)
        fl = round(floating[p], 2)
        exp = round(fx + fl, 2)
        lb = loan_buckets.get(p, {})
        points.append(
            IncomeExpensePoint(
                period=p,
                income=inc,
                fixed=fx,
                floating=fl,
                expense=exp,
                net=round(inc - exp, 2),
                loan_repayment=round(lb.get("principal", 0.0) + lb.get("interest", 0.0), 2),
            )
        )

    # Summary nets each category over the whole window before flooring, so
    # cross-month offsets within the year resolve (≠ sum of the per-month points).
    total_income = 0.0
    total_expense = 0.0
    for cat, value in window_net.items():
        t = norm_type(cat_type[cat])
        if t in INCOME_MAIN_TYPES:
            total_income += floor_income(value)
        elif t in EXPENSE_MAIN_TYPES:
            total_expense += floor_expense(value)
    total_income = round(total_income, 2)
    total_expense = round(total_expense, 2)
    net_total = round(total_income - total_expense, 2)
    savings_rate = round(net_total / total_income, 4) if total_income else 0.0
    return IncomeExpenseReportRead(
        type=type,
        points=points,
        summary=IncomeExpenseSummary(
            total_income=total_income,
            total_expense=total_expense,
            net=net_total,
            savings_rate=savings_rate,
        ),
    )


def _unrealized_by_period(
    session: Session,
    type: Literal["monthly", "yearly"],
    periods: list[str],
) -> dict[str, float]:
    """Per-period change in unrealized P&L: Δ of Σ (market value − cost) × fx_rate.

    Sums every revaluable asset class from its monthly snapshot — stocks
    (``price`` = close × qty), real estate (``market_value``) and insurance
    (``surrender_value``) — each against its ``cost``. For each period we take the
    latest snapshot per asset *as of* that period's anchor month (carrying forward
    unsettled months) and report the change from the prior anchor, so an asset
    held across the window contributes only its in-window value move, not its
    whole accumulated gain. Estate/insurance only move the needle once a real
    value is recorded — until then their snapshot value equals cost (Δ = 0).
    """
    # (snapshot model, attribute holding the market value) per asset class.
    sources = [
        (StockNetValueHistory, "price"),
        (EstateNetValueHistory, "market_value"),
        (InsuranceNetValueHistory, "surrender_value"),
    ]
    by_source = [
        (list(session.exec(select(model)).all()), attr) for model, attr in sources
    ]

    def unrealized_as_of(anchor_month: str) -> float:
        total = 0.0
        for rows, attr in by_source:
            eligible = [r for r in rows if r.vesting_month <= anchor_month]
            latest = _latest_per_entity(eligible, key=lambda r: r.id)
            total += sum((getattr(r, attr) - r.cost) * r.fx_rate for r in latest)
        return total

    if type == "monthly":
        anchors = list(periods)
        prev_anchor = shift_month(periods[0], -1)
    else:
        anchors = [f"{y}12" for y in periods]
        prev_anchor = f"{int(periods[0]) - 1}12"

    out: dict[str, float] = {}
    prev_u = unrealized_as_of(prev_anchor)
    for p, anchor in zip(periods, anchors):
        u = unrealized_as_of(anchor)
        out[p] = u - prev_u
        prev_u = u
    return out


def get_income_statement(
    session: Session,
    type: Literal["monthly", "yearly"],
    vesting_month: str,
) -> IncomeStatementReportRead:
    """Comprehensive income statement (綜合損益表) — three sections per period.

    一、本業損益 = active income (``income`` type only) − living expenses
    (fixed + floating). 二、投資損益 = 孳息 (``passive``) + realized capital gains
    (booked ``資本利得`` journals) + the period change in unrealized market value.
    三、綜合損益 = operating_net + investment_net.

    Income/expense are netted per category then floored at 0 per category (a
    reimbursed 代買 / mis-typed inflow can neither inflate expense nor cancel a
    category); ``passive`` is floored as income. Realized-gain journals are pulled
    out *by Code_Data name before* the income/expense netting, so they can never
    be double-counted no matter how 資本利得 is typed; realized gains stay signed
    (a loss lowers the section). Per-period points floor within each period; the
    summary nets each category across the whole window (cross-month 代買 offsets
    resolve), so it can differ from the sum of the points.
    """
    periods, bucket_of, start_vm, end_vm = _period_window(type, vesting_month)
    journals = list_journals_by_range(session, start_vm, end_vm)
    fx_cache: dict[tuple[str, str], float] = {}

    # Realized capital-gain journals, identified by Code_Data name (robust to
    # whatever action_main_type they carry) and excluded from the income netting.
    code_name = {c.code_id: c.name for c in session.exec(select(CodeData)).all()}
    realized_codes = {
        code_id for code_id, name in code_name.items() if name in REALIZED_GAIN_NAMES
    }

    def is_realized(j: Journal) -> bool:
        return j.action_main in realized_codes or (
            j.action_sub is not None and j.action_sub in realized_codes
        )

    operating_journals = [j for j in journals if not is_realized(j)]
    realized_journals = [j for j in journals if is_realized(j)]

    # ---- 本業 (active income) + 孳息 (passive) + 生活支出 ----
    net, cat_type = category_net_by_bucket(
        operating_journals,
        bucket_of=lambda j: bucket_of(j.vesting_month),
        amount_of=lambda j: journal_amount_twd(session, j, fx_cache),
    )
    active = {p: 0.0 for p in periods}
    fixed = {p: 0.0 for p in periods}
    floating = {p: 0.0 for p in periods}
    dividend = {p: 0.0 for p in periods}
    window_net: dict[str, float] = defaultdict(float)
    for (bucket, cat), value in net.items():
        window_net[cat] += value
        if bucket not in active:
            continue
        t = norm_type(cat_type[cat])
        if t in ACTIVE_INCOME_TYPES:
            active[bucket] += floor_income(value)
        elif t in PASSIVE_INCOME_TYPES:
            dividend[bucket] += floor_income(value)
        elif t == "fixed":
            fixed[bucket] += floor_expense(value)
        elif t == "floating":
            floating[bucket] += floor_expense(value)
        # invest / transfer intentionally excluded

    # ---- 已實現資本利得: signed sum per period (a loss lowers it) ----
    realized = {p: 0.0 for p in periods}
    for j in realized_journals:
        b = bucket_of(j.vesting_month)
        if b in realized:
            realized[b] += journal_amount_twd(session, j, fx_cache)

    # ---- 未實現市值變動 (stocks only) ----
    unrealized = _unrealized_by_period(session, type, periods)

    # ---- 貸款利息 (operating cost, sourced solely from Loan_Journal) ----
    # The loan-repayment Journal is report-neutral, so interest enters the income
    # statement only here (no double-count). Same source as get_cash_flow.
    loan_by_id = {loan.loan_id: loan for loan in session.exec(select(Loan)).all()}
    loan_interest = {p: 0.0 for p in periods}
    for lr in session.exec(select(LoanJournal)).all():
        month = (lr.excute_date or "")[:6]
        if not (start_vm <= month <= end_vm):
            continue
        b = bucket_of(month)
        if b not in loan_interest:
            continue
        if (lr.loan_excute_type or "").strip().lower() in {"interest", "fee"}:
            loan_interest[b] += _loanjournal_amount_twd(session, lr, loan_by_id, fx_cache)

    points: list[IncomeStatementPoint] = []
    for p in periods:
        ai = round(active[p], 2)
        fx = round(fixed[p], 2)
        fl = round(floating[p], 2)
        li = round(loan_interest[p], 2)
        op = round(ai - fx - fl - li, 2)
        dv = round(dividend[p], 2)
        rz = round(realized[p], 2)
        ur = round(unrealized[p], 2)
        inv = round(dv + rz + ur, 2)
        points.append(
            IncomeStatementPoint(
                period=p,
                active_income=ai,
                fixed=fx,
                floating=fl,
                loan_interest=li,
                operating_net=op,
                dividend=dv,
                realized=rz,
                unrealized=ur,
                investment_net=inv,
                comprehensive_net=round(op + inv, 2),
            )
        )

    # ---- Summary: net each category across the whole window before flooring ----
    s_active = s_fixed = s_floating = s_dividend = 0.0
    for cat, value in window_net.items():
        t = norm_type(cat_type[cat])
        if t in ACTIVE_INCOME_TYPES:
            s_active += floor_income(value)
        elif t in PASSIVE_INCOME_TYPES:
            s_dividend += floor_income(value)
        elif t == "fixed":
            s_fixed += floor_expense(value)
        elif t == "floating":
            s_floating += floor_expense(value)
    s_realized = sum(
        journal_amount_twd(session, j, fx_cache) for j in realized_journals
    )
    s_unrealized = sum(unrealized.values())  # telescopes to U(last) − U(base)

    s_loan_interest = round(sum(loan_interest.values()), 2)

    s_active = round(s_active, 2)
    s_fixed = round(s_fixed, 2)
    s_floating = round(s_floating, 2)
    s_operating = round(s_active - s_fixed - s_floating - s_loan_interest, 2)
    s_dividend = round(s_dividend, 2)
    s_realized = round(s_realized, 2)
    s_unrealized = round(s_unrealized, 2)
    s_investment = round(s_dividend + s_realized + s_unrealized, 2)
    return IncomeStatementReportRead(
        type=type,
        points=points,
        summary=IncomeStatementSummary(
            active_income=s_active,
            fixed=s_fixed,
            floating=s_floating,
            loan_interest=s_loan_interest,
            operating_net=s_operating,
            dividend=s_dividend,
            realized=s_realized,
            unrealized=s_unrealized,
            investment_net=s_investment,
            comprehensive_net=round(s_operating + s_investment, 2),
        ),
    )


def get_expenditure_composition(
    session: Session,
    type: Literal["monthly", "yearly"],
    vesting_month: str,
) -> ExpenditureCompositionRead:
    """Category → subcategory tree of expense magnitude over the window.

    Only Fixed/Floating rows are counted (income/invest/transfer excluded). Each
    category's signed cash flow is netted then floored at 0 (``floor_expense``),
    so a category reimbursed to a net inflow (代買) or carrying a mis-typed inflow
    drops out instead of inflating the tree. Amounts are FX-converted; labels
    resolve ``action_main``/``action_sub`` codes to ``Code_Data.name``. Each
    node's ``share`` is a percentage of the grand total; a synthetic "未細分"
    remainder reconciles partly sub-categorized categories to their total.
    """
    _, _, start_vm, end_vm = _period_window(type, vesting_month)
    journals = list_journals_by_range(session, start_vm, end_vm)
    codes = {c.code_id: c for c in session.exec(select(CodeData)).all()}
    fx_cache: dict[tuple[str, str], float] = {}

    cat_net: dict[str, float] = defaultdict(float)
    cat_type: dict[str, str] = {}
    sub_net: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for j in journals:
        if norm_type(j.action_main_type) not in EXPENSE_MAIN_TYPES:
            continue
        amount = journal_amount_twd(session, j, fx_cache)  # signed
        cat = j.action_main
        cat_net[cat] += amount
        cat_type.setdefault(cat, j.action_main_type)
        if j.action_sub:
            sub_net[cat][j.action_sub] += amount

    # Floor each category's net; net-inflow / net-zero categories drop out.
    cat_amount: dict[str, float] = {
        cat: floor_expense(value) for cat, value in cat_net.items()
    }
    cat_amount = {cat: amt for cat, amt in cat_amount.items() if amt > 0.005}
    total = sum(cat_amount.values())

    def share(value: float) -> float:
        return round(value * 100 / total, 2) if total else 0.0

    def name_of(code: str) -> str:
        row = codes.get(code)
        return row.name if row is not None else code

    categories: list[ExpenditureCategoryNode] = []
    for cat in sorted(cat_amount, key=lambda c: cat_amount[c], reverse=True):
        subs = {
            sc: floor_expense(value)
            for sc, value in sub_net.get(cat, {}).items()
        }
        subs = {sc: amt for sc, amt in subs.items() if amt > 0.005}
        children: list[ExpenditureSubNode] = [
            ExpenditureSubNode(
                code=sc,
                name=name_of(sc),
                amount=round(subs[sc], 2),
                share=share(subs[sc]),
            )
            for sc in sorted(subs, key=lambda s: subs[s], reverse=True)
        ]
        if children:
            remainder = cat_amount[cat] - sum(subs.values())
            if remainder > 0.005:
                children.append(
                    ExpenditureSubNode(
                        code="",
                        name="未細分",
                        amount=round(remainder, 2),
                        share=share(remainder),
                    )
                )
        categories.append(
            ExpenditureCategoryNode(
                code=cat,
                name=name_of(cat),
                type=cat_type[cat],
                amount=round(cat_amount[cat], 2),
                share=share(cat_amount[cat]),
                children=children,
            )
        )

    fixed_total = sum(
        v for c, v in cat_amount.items() if norm_type(cat_type[c]) == "fixed"
    )
    return ExpenditureCompositionRead(
        total=round(total, 2),
        fixed_total=round(fixed_total, 2),
        floating_total=round(total - fixed_total, 2),
        categories=categories,
    )


def get_budget_variance(session: Session, year: str) -> BudgetVarianceRead:
    """Annual budget vs actual per expense category for the calendar ``year``.

    Expected: ``Budget.annual_amount`` for annual-event categories (which budget
    as a single yearly envelope), else the sum of ``expected01..12``. Actual: the
    year's FX-converted Fixed/Floating journals grouped by ``action_main``.
    Annual-event categories are *included* here (unlike the monthly budget view)
    because a yearly review should account for lumpy once-a-year costs. Income,
    invest and transfer categories are excluded. ``projected_total`` annualizes
    the actual by the latest month carrying data, so a part-year reads as a
    run-rate rather than an apparent under-spend.
    """
    budgets = list(
        session.exec(select(Budget).where(Budget.budget_year == year)).all()
    )
    expected_by_code: dict[str, float] = {}
    name_by_code: dict[str, str] = {}
    type_by_code: dict[str, str] = {}
    for b in budgets:
        if norm_type(b.code_type) not in EXPENSE_MAIN_TYPES:
            continue
        if b.annual_amount is not None:
            expected = b.annual_amount
        else:
            expected = sum(
                float(getattr(b, f"expected{m:02d}") or 0.0) for m in range(1, 13)
            )
        expected_by_code[b.category_code] = expected
        name_by_code[b.category_code] = b.category_name
        type_by_code[b.category_code] = b.code_type

    journals = list_journals_by_range(session, f"{year}01", f"{year}12")
    codes = {c.code_id: c for c in session.exec(select(CodeData)).all()}
    fx_cache: dict[tuple[str, str], float] = {}
    net_by_code: dict[str, float] = defaultdict(float)
    months_with_data: set[int] = set()
    for j in journals:
        if norm_type(j.action_main_type) not in EXPENSE_MAIN_TYPES:
            continue
        net_by_code[j.action_main] += journal_amount_twd(session, j, fx_cache)  # signed
        vm = j.vesting_month or ""
        if len(vm) == 6:
            months_with_data.add(int(vm[4:6]))
        if j.action_main not in name_by_code:
            row = codes.get(j.action_main)
            name_by_code[j.action_main] = row.name if row is not None else j.action_main
            type_by_code[j.action_main] = (
                row.code_type if row is not None else j.action_main_type
            )
    # Floor each category's annual net: a reimbursed/mis-typed net inflow → 0.
    actual_by_code: dict[str, float] = {
        code: floor_expense(value) for code, value in net_by_code.items()
    }

    rows: list[BudgetVarianceRow] = []
    for code in sorted(
        set(expected_by_code) | set(actual_by_code),
        key=lambda c: actual_by_code.get(c, 0.0),
        reverse=True,
    ):
        expected = round(expected_by_code.get(code, 0.0), 2)
        actual = round(actual_by_code.get(code, 0.0), 2)
        rows.append(
            BudgetVarianceRow(
                code=code,
                name=name_by_code.get(code, code),
                type=type_by_code.get(code, ""),
                expected=expected,
                actual=actual,
                diff=round(actual - expected, 2),
                usage_rate=round(actual / expected, 4) if expected else 0.0,
            )
        )

    total_expected = round(sum(r.expected for r in rows), 2)
    total_actual = round(sum(r.actual for r in rows), 2)
    elapsed = max(months_with_data) if months_with_data else 0
    projected_total = (
        round(total_actual / elapsed * 12, 2) if 0 < elapsed < 12 else total_actual
    )
    return BudgetVarianceRead(
        year=year,
        rows=rows,
        summary=BudgetVarianceSummary(
            total_expected=total_expected,
            total_actual=total_actual,
            total_diff=round(total_actual - total_expected, 2),
            usage_rate=round(total_actual / total_expected, 4) if total_expected else 0.0,
            elapsed_months=elapsed,
            projected_total=projected_total,
        ),
    )


def get_cash_flow(
    session: Session,
    type: Literal["monthly", "yearly"],
    vesting_month: str,
) -> CashFlowRead:
    """Personal cash-flow statement split into 生活 / 投資 / 債務, per period.

    - 生活 (operating): income (+) − living expenses (Fixed/Floating, −) − loan
      interest/fee (from LoanJournal, −).
    - 投資 (investing): signed Invest journals (buy negative, sell positive).
    - 債務 (financing): new borrowing (LoanJournal ``increment``, +) − principal
      repayment (LoanJournal ``principal``, −).

    Self-transfers are excluded (net-zero between own accounts; the type is also
    reused for gifts). Credit-card spend is counted once here as an operating
    outflow — settlement is a balance snapshot, not re-counted. Loan servicing is
    sourced solely from LoanJournal (it is not duplicated as main-Journal rows),
    so interest and principal are never double-counted. All amounts FX-converted.

    Returns a per-period series (``points``) plus a window ``summary``. Cash flow
    is a pure signed sum — no floor / cross-month netting — so each period is
    independent and the summary equals the sum of the points.
    """
    periods, bucket_of, start_vm, end_vm = _period_window(type, vesting_month)
    journals = list_journals_by_range(session, start_vm, end_vm)
    fx_cache: dict[tuple[str, str], float] = {}

    income = {p: 0.0 for p in periods}
    living = {p: 0.0 for p in periods}  # signed (negative)
    investing = {p: 0.0 for p in periods}  # signed
    for j in journals:
        b = bucket_of(j.vesting_month)
        if b not in income:
            continue
        t = norm_type(j.action_main_type)
        amount = journal_amount_twd(session, j, fx_cache)
        if t in INCOME_MAIN_TYPES:
            income[b] += amount
        elif t in EXPENSE_MAIN_TYPES:
            living[b] += amount
        elif t in INVEST_MAIN_TYPES:
            investing[b] += amount
        # transfer excluded

    loan_by_id = {loan.loan_id: loan for loan in session.exec(select(Loan)).all()}
    loan_interest = {p: 0.0 for p in periods}
    principal = {p: 0.0 for p in periods}
    increment = {p: 0.0 for p in periods}
    for lr in session.exec(select(LoanJournal)).all():
        month = (lr.excute_date or "")[:6]
        if not (start_vm <= month <= end_vm):
            continue
        b = bucket_of(month)
        if b not in loan_interest:
            continue
        magnitude = _loanjournal_amount_twd(session, lr, loan_by_id, fx_cache)
        et = (lr.loan_excute_type or "").strip().lower()
        if et in {"interest", "fee"}:
            loan_interest[b] += magnitude
        elif et == "principal":
            principal[b] += magnitude
        elif et == "increment":
            increment[b] += magnitude

    points: list[CashFlowPoint] = []
    for p in periods:
        op = round(income[p] + living[p] - loan_interest[p], 2)
        inv = round(investing[p], 2)
        fin = round(increment[p] - principal[p], 2)
        points.append(
            CashFlowPoint(
                period=p,
                operating=op,
                investing=inv,
                financing=fin,
                net_change=round(op + inv + fin, 2),
            )
        )

    # ---- Window summary: net each component across the whole window ----
    s_income = round(sum(income.values()), 2)
    s_living = round(sum(living.values()), 2)
    s_investing = round(sum(investing.values()), 2)
    s_interest = round(sum(loan_interest.values()), 2)
    s_principal = round(sum(principal.values()), 2)
    s_increment = round(sum(increment.values()), 2)

    operating_net = round(s_income + s_living - s_interest, 2)
    investing_net = s_investing
    financing_net = round(s_increment - s_principal, 2)
    net_change = round(operating_net + investing_net + financing_net, 2)

    operating_items = [
        CashFlowItem(label="收入", amount=s_income),
        CashFlowItem(label="生活支出", amount=s_living),
    ]
    if s_interest:
        operating_items.append(CashFlowItem(label="貸款利息", amount=round(-s_interest, 2)))

    financing_items: list[CashFlowItem] = []
    if s_increment:
        financing_items.append(CashFlowItem(label="新增借款", amount=s_increment))
    if s_principal:
        financing_items.append(CashFlowItem(label="償還本金", amount=round(-s_principal, 2)))

    activities = [
        CashFlowActivity(
            key="operating", label="生活", net=operating_net, items=operating_items
        ),
        CashFlowActivity(
            key="investing",
            label="投資",
            net=investing_net,
            items=[CashFlowItem(label="投資淨額", amount=s_investing)],
        ),
        CashFlowActivity(
            key="financing", label="債務", net=financing_net, items=financing_items
        ),
    ]
    summary = CashFlowSummary(activities=activities, net_change=net_change)
    return CashFlowRead(type=type, points=points, summary=summary)


def _pay_way_name(session: Session, journal: Journal) -> str:
    """Human-readable payment source name for a journal (account or card)."""
    if journal.spend_way_table == "Account":
        try:
            pk = int(journal.spend_way)
        except (TypeError, ValueError):
            return journal.spend_way
        account = session.get(Account, pk)
        return account.name if account is not None else journal.spend_way
    if journal.spend_way_table == "Credit_Card":
        card = session.get(CreditCard, journal.spend_way)
        return card.card_name if card is not None else journal.spend_way
    return journal.spend_way


def get_expense_insights(
    session: Session, year: str, top_n: int = 10
) -> ExpenseInsightsRead:
    """Year-over-year change per expense category + the year's largest expenses.

    YoY compares the calendar ``year`` against the prior year, per ``action_main``
    category, ordered by the absolute change so the biggest movers surface first.
    ``largest`` lists the top-N individual Fixed/Floating transactions by
    FX-converted magnitude, each drilled down to date / category / amount /
    payment source / note.
    """
    codes = {c.code_id: c for c in session.exec(select(CodeData)).all()}
    fx_cache: dict[tuple[str, str], float] = {}

    def name_of(code: str) -> str:
        row = codes.get(code)
        return row.name if row is not None else code

    def type_of(code: str) -> str:
        row = codes.get(code)
        return row.code_type if row is not None else ""

    def expense_by_code(journals: list[Journal]) -> dict[str, float]:
        net: dict[str, float] = defaultdict(float)
        for j in journals:
            if norm_type(j.action_main_type) not in EXPENSE_MAIN_TYPES:
                continue
            net[j.action_main] += journal_amount_twd(session, j, fx_cache)  # signed
        return {code: floor_expense(value) for code, value in net.items()}

    current_journals = list_journals_by_range(session, f"{year}01", f"{year}12")
    prev_year = str(int(year) - 1)
    prev_journals = list_journals_by_range(session, f"{prev_year}01", f"{prev_year}12")
    current = expense_by_code(current_journals)
    previous = expense_by_code(prev_journals)

    yoy: list[YoYRow] = []
    for code in sorted(
        set(current) | set(previous),
        key=lambda c: abs(current.get(c, 0.0) - previous.get(c, 0.0)),
        reverse=True,
    ):
        cur = round(current.get(code, 0.0), 2)
        prev = round(previous.get(code, 0.0), 2)
        yoy.append(
            YoYRow(
                code=code,
                name=name_of(code),
                type=type_of(code),
                current=cur,
                previous=prev,
                delta=round(cur - prev, 2),
                yoy_rate=round((cur - prev) / prev, 4) if prev else 0.0,
            )
        )

    # Largest individual outflows only — a positive-spending row (income, a
    # reimbursed 代買, or a mis-typed inflow) is not an expense, so exclude it.
    expense_txns: list[tuple[Journal, float]] = []
    for j in current_journals:
        if norm_type(j.action_main_type) not in EXPENSE_MAIN_TYPES:
            continue
        amount = journal_amount_twd(session, j, fx_cache)
        if amount < 0:
            expense_txns.append((j, -amount))
    expense_txns.sort(key=lambda pair: pair[1], reverse=True)
    largest = [
        LargeTxn(
            date=j.spend_date,
            category=name_of(j.action_main),
            amount=round(amount, 2),
            pay_way=_pay_way_name(session, j),
            note=j.note,
        )
        for j, amount in expense_txns[:top_n]
    ]

    return ExpenseInsightsRead(year=year, yoy=yoy, largest=largest)


def get_asset_breakdown(session: Session) -> AssetBreakdownRead:
    """Latest-month totals per bucket; ``other`` aggregates ``OtherAsset`` of type ``other``."""
    accounts_rows = list(session.exec(select(AccountBalance)).all())
    accounts_total = sum(
        r.balance * r.fx_rate
        for r in _latest_per_entity(accounts_rows, key=lambda r: r.id)
        if r.is_calculate == "Y"
    )

    stock_rows = list(session.exec(select(StockNetValueHistory)).all())
    stocks_total = sum(
        r.price * r.fx_rate
        for r in _latest_per_entity(stock_rows, key=lambda r: r.id)
    )

    estate_rows = list(session.exec(select(EstateNetValueHistory)).all())
    estates_total = sum(
        r.market_value * r.fx_rate
        for r in _latest_per_entity(estate_rows, key=lambda r: r.id)
    )

    insurance_rows = list(session.exec(select(InsuranceNetValueHistory)).all())
    insurances_total = sum(
        r.surrender_value * r.fx_rate
        for r in _latest_per_entity(insurance_rows, key=lambda r: r.id)
    )

    other_assets = list(
        session.exec(select(OtherAsset).where(OtherAsset.asset_type == "other")).all()
    )
    other_total = float(len(other_assets)) and 0.0  # placeholder; OtherAsset has no value column
    other_total = 0.0

    bucket_amounts = {
        "accounts": accounts_total,
        "stocks": stocks_total,
        "estates": estates_total,
        "insurances": insurances_total,
        "other": other_total,
    }
    total = sum(bucket_amounts.values())
    items = []
    for bucket_type, amount in bucket_amounts.items():
        share = round(amount * 100 / total, 2) if total else 0.0
        items.append(
            AssetShare(type=bucket_type, amount=round(amount, 2), share=share)
        )
    return AssetBreakdownRead(total=round(total, 2), items=items)


def get_stock_allocation(session: Session) -> StockAllocationRead:
    """Latest-month stock value split by ``Stock_Journal.category_id``.

    Mirrors ``get_asset_breakdown``'s stock valuation (``price * fx_rate`` on the
    latest snapshot per holding) so the per-category amounts reconcile with the
    ``stocks`` bucket there. Holdings with a null or dangling category collapse
    into the synthetic "未分類" (unclassified) share. Items are ordered by
    ``category_index`` with the unclassified share last.
    """
    unclassified = "未分類"

    stock_rows = list(session.exec(select(StockNetValueHistory)).all())
    latest = _latest_per_entity(stock_rows, key=lambda r: r.id)

    category_of = {
        s.stock_id: s.category_id for s in session.exec(select(StockJournal)).all()
    }
    categories = list(session.exec(select(StockCategory)).all())
    name_of = {c.category_id: c.name for c in categories}
    index_of = {c.category_id: c.category_index for c in categories}

    amounts: dict[str | None, float] = {}
    for r in latest:
        cid = category_of.get(r.id)
        if cid is not None and cid not in name_of:
            cid = None  # dangling reference → unclassified
        amounts[cid] = amounts.get(cid, 0.0) + r.price * r.fx_rate

    total = sum(amounts.values())
    ordered = sorted(
        amounts.items(),
        key=lambda kv: (kv[0] is None, index_of.get(kv[0], 0), kv[0] or ""),
    )
    items = [
        StockAllocationShare(
            category_id=cid,
            category_name=name_of[cid] if cid is not None else unclassified,
            amount=round(amount, 2),
            share=round(amount * 100 / total, 2) if total else 0.0,
        )
        for cid, amount in ordered
    ]
    return StockAllocationRead(total=round(total, 2), items=items)
