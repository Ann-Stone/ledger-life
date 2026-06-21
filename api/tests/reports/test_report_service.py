"""BE-025 — report_service unit tests."""
from __future__ import annotations

from sqlmodel import Session

from app.models.assets.loan import LoanJournal
from app.models.dashboard.fx_rate import FXRate
from app.models.monthly_report.account_balance import AccountBalance
from app.models.monthly_report.credit_card_balance import CreditCardBalance
from app.models.monthly_report.estate_net_value_history import EstateNetValueHistory
from app.models.monthly_report.insurance_net_value_history import (
    InsuranceNetValueHistory,
)
from app.models.monthly_report.journal import Journal
from app.models.monthly_report.loan_balance import LoanBalance
from app.models.monthly_report.stock_net_value_history import StockNetValueHistory
from app.models.settings.account import Account
from app.models.settings.budget import Budget
from app.models.settings.code_data import CodeData
from app.models.settings.credit_card import CreditCard
from app.services.fx_lookup import fx_rate_for_month
from app.services.report_service import (
    get_asset_breakdown,
    get_balance_sheet,
    get_budget_variance,
    get_cash_flow,
    get_expense_insights,
    get_expenditure_composition,
    get_expenditure_trend,
    get_income_expense_report,
    journal_amount_twd,
    list_journals_by_range,
)


def test_fx_rate_for_month_fallback(session: Session) -> None:
    # No row at all → 1.0
    assert fx_rate_for_month(session, "USD", "202604") == 1.0
    # Row outside the window → fallback
    session.add(FXRate(import_date="20270101", code="USD", buy_rate=33.0))
    session.commit()
    assert fx_rate_for_month(session, "USD", "202604") == 33.0
    # Row inside window beats fallback
    session.add(FXRate(import_date="20260415", code="USD", buy_rate=31.5))
    session.commit()
    assert fx_rate_for_month(session, "USD", "202604") == 31.5
    # Base currency short-circuits to 1.0
    assert fx_rate_for_month(session, "TWD", "202604") == 1.0


def _seed_balance_fixture(session: Session) -> None:
    session.add(
        AccountBalance(
            vesting_month="202604",
            id="A1",
            name="TWD Bank",
            balance=100000.0,
            fx_code="TWD",
            fx_rate=1.0,
            is_calculate="Y",
        )
    )
    session.add(
        AccountBalance(
            vesting_month="202604",
            id="A2",
            name="USD Bank",
            balance=1000.0,
            fx_code="USD",
            fx_rate=32.0,
            is_calculate="Y",
        )
    )
    session.add(
        StockNetValueHistory(
            vesting_month="202604",
            id="S1",
            asset_id="AC1",
            stock_code="AAPL",
            stock_name="Apple",
            amount=10.0,
            price=2000.0,  # market value already
            cost=1500.0,
            fx_code="USD",
            fx_rate=32.0,
        )
    )
    session.add(
        EstateNetValueHistory(
            vesting_month="202604",
            id="E1",
            asset_id="AC2",
            name="Condo",
            market_value=500000.0,
            cost=400000.0,
            estate_status="hold",
            fx_code="TWD",
            fx_rate=1.0,
        )
    )
    session.add(
        InsuranceNetValueHistory(
            vesting_month="202604",
            id="I1",
            asset_id="AC3",
            name="Whole Life",
            surrender_value=2000.0,
            cost=1500.0,
            fx_code="USD",
            fx_rate=32.0,
        )
    )
    session.add(
        LoanBalance(
            vesting_month="202604",
            id="L1",
            name="Mortgage",
            balance=-200000.0,
            cost=0.0,
            fx_code="TWD",
            fx_rate=1.0,
        )
    )
    session.add(
        CreditCardBalance(
            vesting_month="202604",
            id="CC1",
            name="Visa",
            balance=-3000.0,
            fx_rate=1.0,
        )
    )
    session.commit()


def test_get_balance_sheet_golden(session: Session) -> None:
    _seed_balance_fixture(session)

    sheet = get_balance_sheet(session)
    # accounts: 100000 + 1000*32 = 132000
    accounts_total = sum(line.amount for line in sheet.assets.accounts)
    assert accounts_total == 132000.0
    # stocks: 2000 * 32 = 64000
    assert sheet.assets.stocks[0].amount == 64000.0
    # estates: 500000
    assert sheet.assets.estates[0].amount == 500000.0
    # insurances: 2000 * 32 = 64000
    assert sheet.assets.insurances[0].amount == 64000.0
    # loans + cc: -200000 + -3000
    loans_total = sum(line.amount for line in sheet.liabilities.loans)
    cc_total = sum(line.amount for line in sheet.liabilities.credit_cards)
    assert loans_total == -200000.0
    assert cc_total == -3000.0
    # net worth = 132000 + 64000 + 500000 + 64000 - 200000 - 3000 = 557000
    assert sheet.net_worth == 557000.0

    # original_amount = pre-FX native amount (base-currency entities echo `amount`)
    accounts_by_name = {line.name: line for line in sheet.assets.accounts}
    assert accounts_by_name["TWD Bank"].original_amount == 100000.0
    assert accounts_by_name["USD Bank"].original_amount == 1000.0
    assert sheet.assets.stocks[0].original_amount == 2000.0
    assert sheet.assets.estates[0].original_amount == 500000.0
    assert sheet.assets.insurances[0].original_amount == 2000.0
    assert sheet.liabilities.loans[0].original_amount == -200000.0
    assert sheet.liabilities.credit_cards[0].original_amount == -3000.0
    # TWD entities expose their currency explicitly now (was hardcoded base).
    assert sheet.assets.estates[0].currency == "TWD"
    assert sheet.liabilities.loans[0].currency == "TWD"


def test_get_balance_sheet_estate_and_loan_foreign_currency(session: Session) -> None:
    # Overseas property + foreign loan held in USD: amount is FX-converted to
    # base currency, original_amount keeps the native figure.
    session.add(
        EstateNetValueHistory(
            vesting_month="202604",
            id="E-US",
            asset_id="AC-REAL-US",
            name="Overseas Condo",
            market_value=300000.0,  # native USD
            cost=250000.0,
            estate_status="hold",
            fx_code="USD",
            fx_rate=32.0,
        )
    )
    session.add(
        LoanBalance(
            vesting_month="202604",
            id="L-US",
            name="US Mortgage",
            balance=-100000.0,  # native USD
            cost=120000.0,
            fx_code="USD",
            fx_rate=32.0,
        )
    )
    session.commit()

    sheet = get_balance_sheet(session)
    estate = sheet.assets.estates[0]
    assert estate.currency == "USD"
    assert estate.original_amount == 300000.0
    assert estate.amount == 9600000.0  # 300000 * 32
    loan = sheet.liabilities.loans[0]
    assert loan.currency == "USD"
    assert loan.original_amount == -100000.0
    assert loan.amount == -3200000.0  # -100000 * 32


def test_get_balance_sheet_picks_latest_month(session: Session) -> None:
    session.add(
        AccountBalance(
            vesting_month="202603",
            id="A1",
            name="TWD Bank",
            balance=50000.0,
            fx_code="TWD",
            fx_rate=1.0,
            is_calculate="Y",
        )
    )
    session.add(
        AccountBalance(
            vesting_month="202604",
            id="A1",
            name="TWD Bank",
            balance=70000.0,
            fx_code="TWD",
            fx_rate=1.0,
            is_calculate="Y",
        )
    )
    session.commit()

    sheet = get_balance_sheet(session)
    assert sheet.assets.accounts[0].amount == 70000.0


def test_get_expenditure_trend_monthly_golden(session: Session) -> None:
    # Anchor 202604 → window 202505..202604
    session.add(
        Journal(
            vesting_month="202604",
            spend_date="20260410",
            spend_way="A1",
            spend_way_type="account",
            spend_way_table="Account",
            action_main="E01",
            action_main_type="Floating",
            action_main_table="Code_Data",
            spending=-100.0,
        )
    )
    session.add(
        Journal(
            vesting_month="202604",
            spend_date="20260411",
            spend_way="A1",
            spend_way_type="account",
            spend_way_table="Account",
            action_main="F01",
            action_main_type="Fixed",
            action_main_table="Code_Data",
            spending=-200.0,
        )
    )
    # Income excluded
    session.add(
        Journal(
            vesting_month="202604",
            spend_date="20260412",
            spend_way="A1",
            spend_way_type="account",
            spend_way_table="Account",
            action_main="I01",
            action_main_type="Income",
            action_main_table="Code_Data",
            spending=5000.0,
        )
    )
    # Out-of-window month
    session.add(
        Journal(
            vesting_month="202410",
            spend_date="20241010",
            spend_way="A1",
            spend_way_type="account",
            spend_way_table="Account",
            action_main="E01",
            action_main_type="Floating",
            action_main_table="Code_Data",
            spending=-999.0,
        )
    )
    session.commit()

    trend = get_expenditure_trend(session, "monthly", "202604")
    assert trend.type == "monthly"
    assert len(trend.points) == 12
    by_period = {p.period: p.amount for p in trend.points}
    assert by_period["202604"] == 300.0
    assert by_period["202603"] == 0.0
    assert "202410" not in by_period


def test_get_expenditure_trend_yearly_golden(session: Session) -> None:
    session.add(
        Journal(
            vesting_month="202508",
            spend_date="20250810",
            spend_way="A1",
            spend_way_type="account",
            spend_way_table="Account",
            action_main="E01",
            action_main_type="Floating",
            action_main_table="Code_Data",
            spending=-150.0,
        )
    )
    session.add(
        Journal(
            vesting_month="202412",
            spend_date="20241210",
            spend_way="A1",
            spend_way_type="account",
            spend_way_table="Account",
            action_main="F01",
            action_main_type="Fixed",
            action_main_table="Code_Data",
            spending=-50.0,
        )
    )
    session.commit()

    trend = get_expenditure_trend(session, "yearly", "202604")
    assert trend.type == "yearly"
    assert len(trend.points) == 10
    by_period = {p.period: p.amount for p in trend.points}
    assert by_period["2025"] == 150.0
    assert by_period["2024"] == 50.0
    assert by_period["2026"] == 0.0


def test_get_asset_breakdown_golden(session: Session) -> None:
    _seed_balance_fixture(session)

    breakdown = get_asset_breakdown(session)
    # totals: 132000 + 64000 + 500000 + 64000 = 760000
    assert breakdown.total == 760000.0
    by_type = {item.type: item for item in breakdown.items}
    assert by_type["accounts"].amount == 132000.0
    assert by_type["stocks"].amount == 64000.0
    assert by_type["estates"].amount == 500000.0
    assert by_type["insurances"].amount == 64000.0
    assert by_type["other"].amount == 0.0
    # Shares sum to ~100
    assert abs(sum(i.share for i in breakdown.items) - 100.0) < 0.05


# ---------- Ticket 0: FX-correct aggregation + range helpers ----------


def _expense_journal(**overrides) -> Journal:
    base = dict(
        vesting_month="202604",
        spend_date="20260410",
        spend_way="A1",
        spend_way_type="account",
        spend_way_table="Account",
        action_main="E01",
        action_main_type="Floating",
        action_main_table="Code_Data",
        spending=-100.0,
    )
    base.update(overrides)
    return Journal(**base)


def test_expenditure_trend_fx_converts_foreign_account(session: Session) -> None:
    # USD account (PK id=7), spend -100 at rate 30 → 3000 TWD.
    session.add(
        Account(
            id=7,
            account_id="USD-1",
            name="USD Bank",
            account_type="bank",
            fx_code="USD",
            is_calculate="Y",
            in_use="Y",
            discount=1.0,
            account_index=1,
        )
    )
    session.add(FXRate(import_date="20260415", code="USD", buy_rate=30.0))
    session.add(_expense_journal(spend_way="7", spending=-100.0))
    session.commit()

    trend = get_expenditure_trend(session, "monthly", "202604")
    by_period = {p.period: p.amount for p in trend.points}
    assert by_period["202604"] == 3000.0


def test_expenditure_trend_fx_converts_foreign_credit_card(session: Session) -> None:
    # USD credit card, spend -50 at rate 30 → 1500 TWD. compute_gain_loss would
    # have missed this (it only converts account-funded rows).
    session.add(
        CreditCard(
            credit_card_id="CC-USD",
            card_name="USD Card",
            fx_code="USD",
            in_use="Y",
            credit_card_index=1,
        )
    )
    session.add(FXRate(import_date="20260415", code="USD", buy_rate=30.0))
    session.add(
        _expense_journal(
            spend_way="CC-USD",
            spend_way_type="credit_card",
            spend_way_table="Credit_Card",
            action_main_type="Fixed",
            spending=-50.0,
        )
    )
    session.commit()

    trend = get_expenditure_trend(session, "monthly", "202604")
    by_period = {p.period: p.amount for p in trend.points}
    assert by_period["202604"] == 1500.0


def test_journal_amount_twd_preserves_sign(session: Session) -> None:
    # Base-currency income returns the signed amount unchanged (positive).
    income = _expense_journal(
        action_main="I01", action_main_type="Income", spending=5000.0
    )
    session.add(income)
    session.commit()
    assert journal_amount_twd(session, income) == 5000.0


def test_list_journals_by_range_is_inclusive(session: Session) -> None:
    for vm, day in [("202601", "20260101"), ("202603", "20260301"), ("202605", "20260501")]:
        session.add(_expense_journal(vesting_month=vm, spend_date=day, spending=-10.0))
    session.commit()
    rows = list_journals_by_range(session, "202602", "202604")
    assert [r.vesting_month for r in rows] == ["202603"]


# ---------- Ticket 1: income statement + savings rate ----------


def test_income_expense_report_monthly_golden(session: Session) -> None:
    # 202604: income 5000, fixed -200, floating -100 → expense 300, net 4700.
    session.add(_expense_journal(action_main="I01", action_main_type="Income", spending=5000.0, spend_date="20260401"))
    session.add(_expense_journal(action_main="F01", action_main_type="Fixed", spending=-200.0, spend_date="20260402"))
    session.add(_expense_journal(action_main="FL01", action_main_type="Floating", spending=-100.0, spend_date="20260403"))
    # invest + transfer must be excluded from income/expense
    session.add(_expense_journal(action_main="INV01", action_main_type="Invest", spending=-1000.0, spend_date="20260404"))
    session.add(_expense_journal(action_main="TRF01", action_main_type="Transfer", spending=-500.0, spend_date="20260405"))
    session.commit()

    report = get_income_expense_report(session, "monthly", "202604")
    assert report.type == "monthly"
    assert len(report.points) == 12
    pt = {p.period: p for p in report.points}["202604"]
    assert pt.income == 5000.0
    assert pt.fixed == 200.0
    assert pt.floating == 100.0
    assert pt.expense == 300.0
    assert pt.net == 4700.0
    assert report.summary.total_income == 5000.0
    assert report.summary.total_expense == 300.0
    assert report.summary.net == 4700.0
    assert report.summary.savings_rate == 0.94  # 4700 / 5000


def test_income_expense_savings_rate_guards_zero_income(session: Session) -> None:
    session.add(_expense_journal(action_main_type="Fixed", spending=-100.0))
    session.commit()
    report = get_income_expense_report(session, "monthly", "202604")
    assert report.summary.total_income == 0.0
    assert report.summary.savings_rate == 0.0


def test_income_expense_type_matching_is_case_insensitive(session: Session) -> None:
    # lowercase casing (monthly-domain / legacy imports) still classifies.
    session.add(_expense_journal(action_main="I01", action_main_type="income", spending=1000.0))
    session.add(_expense_journal(action_main="FL01", action_main_type="floating", spending=-300.0))
    session.commit()
    pt = {p.period: p for p in get_income_expense_report(session, "monthly", "202604").points}["202604"]
    assert pt.income == 1000.0
    assert pt.floating == 300.0
    assert pt.net == 700.0


# ---------- Ticket 2: expenditure composition tree ----------


def test_expenditure_composition_tree_golden(session: Session) -> None:
    session.add(CodeData(code_id="E01", code_type="Floating", name="餐飲", in_use="Y", code_index=1))
    session.add(CodeData(code_id="E0101", code_type="Floating", name="外食", parent_id="E01", in_use="Y", code_index=1))
    session.add(CodeData(code_id="F01", code_type="Fixed", name="房租", in_use="Y", code_index=2))
    # 餐飲: subcategorized 外食 -300 + un-subcategorized -100 → category 400
    session.add(_expense_journal(vesting_month="202603", spend_date="20260301", action_main="E01", action_main_type="Floating", action_sub="E0101", action_sub_type="Floating", action_sub_table="Code_Data", spending=-300.0))
    session.add(_expense_journal(vesting_month="202604", spend_date="20260401", action_main="E01", action_main_type="Floating", spending=-100.0))
    # 房租: -800 fixed, no sub
    session.add(_expense_journal(vesting_month="202605", spend_date="20260501", action_main="F01", action_main_type="Fixed", spending=-800.0))
    # income excluded entirely
    session.add(_expense_journal(vesting_month="202606", spend_date="20260601", action_main="I01", action_main_type="Income", spending=5000.0))
    session.commit()

    comp = get_expenditure_composition(session, "monthly", "202612")
    assert comp.total == 1200.0
    assert comp.fixed_total == 800.0
    assert comp.floating_total == 400.0
    # ordered by amount desc → 房租 (800) then 餐飲 (400)
    assert [c.code for c in comp.categories] == ["F01", "E01"]
    by_code = {c.code: c for c in comp.categories}

    food = by_code["E01"]
    assert food.name == "餐飲"
    assert food.type == "Floating"
    assert food.amount == 400.0
    # children reconcile to category total: 外食 300 + 未細分 remainder 100
    child_amounts = {ch.code: ch.amount for ch in food.children}
    assert child_amounts["E0101"] == 300.0
    assert child_amounts[""] == 100.0
    assert round(sum(ch.amount for ch in food.children), 2) == food.amount

    rent = by_code["F01"]
    assert rent.name == "房租"
    assert rent.children == []  # no sub-codes → leaf category

    # category shares reconcile to ~100% of the grand total
    assert abs(sum(c.share for c in comp.categories) - 100.0) < 0.05


# ---------- Ticket 3: budget vs actual variance ----------


def _budget(code: str, name: str, code_type: str, monthly: float = 0.0, annual: float | None = None) -> Budget:
    return Budget(
        budget_year="2026",
        category_code=code,
        category_name=name,
        code_type=code_type,
        annual_amount=annual,
        **{f"expected{m:02d}": monthly for m in range(1, 13)},
    )


def test_budget_variance_golden(session: Session) -> None:
    session.add(_budget("F01", "居住", "Fixed", monthly=30000.0))  # annual 360000
    session.add(_budget("E01", "餐飲", "Floating", monthly=15000.0))  # annual 180000
    session.add(_budget("INC01", "薪資", "income", monthly=100000.0))  # excluded
    for m in (1, 2, 3):
        session.add(_expense_journal(vesting_month=f"2026{m:02d}", spend_date=f"2026{m:02d}05", action_main="F01", action_main_type="Fixed", spending=-30000.0))
    session.add(_expense_journal(vesting_month="202601", spend_date="20260106", action_main="E01", action_main_type="Floating", spending=-20000.0))
    session.commit()

    rep = get_budget_variance(session, "2026")
    assert rep.year == "2026"
    by_code = {r.code: r for r in rep.rows}
    assert "INC01" not in by_code  # income budget excluded
    assert by_code["F01"].expected == 360000.0
    assert by_code["F01"].actual == 90000.0
    assert by_code["F01"].diff == -270000.0
    assert by_code["F01"].usage_rate == 0.25
    assert by_code["E01"].expected == 180000.0
    assert by_code["E01"].actual == 20000.0
    # ordered by actual desc
    assert [r.code for r in rep.rows] == ["F01", "E01"]
    # summary + run-rate projection (data through month 3)
    assert rep.summary.total_expected == 540000.0
    assert rep.summary.total_actual == 110000.0
    assert rep.summary.elapsed_months == 3
    assert rep.summary.projected_total == round(110000.0 / 3 * 12, 2)


def test_budget_variance_includes_annual_event_envelope(session: Session) -> None:
    # Annual-event category budgets as a single annual_amount, not 12 monthly.
    session.add(_budget("INS01", "保險", "Fixed", monthly=0.0, annual=96000.0))
    session.add(_expense_journal(vesting_month="202603", spend_date="20260315", action_main="INS01", action_main_type="Fixed", spending=-96000.0))
    session.commit()
    ins = {r.code: r for r in get_budget_variance(session, "2026").rows}["INS01"]
    assert ins.expected == 96000.0  # from annual_amount, not 12 × 0
    assert ins.actual == 96000.0
    assert ins.usage_rate == 1.0


# ---------- Ticket 4: cash-flow 生活/投資/債務 ----------


def test_cash_flow_golden(session: Session) -> None:
    # operating: income +5000, fixed -1000, floating -500, loan interest -300
    session.add(_expense_journal(vesting_month="202603", spend_date="20260301", action_main_type="Income", spending=5000.0))
    session.add(_expense_journal(vesting_month="202603", spend_date="20260302", action_main_type="Fixed", spending=-1000.0))
    session.add(_expense_journal(vesting_month="202603", spend_date="20260303", action_main_type="Floating", spending=-500.0))
    # investing: buy -800
    session.add(_expense_journal(vesting_month="202604", spend_date="20260401", action_main_type="Invest", spending=-800.0))
    # transfer excluded
    session.add(_expense_journal(vesting_month="202604", spend_date="20260402", action_main_type="Transfer", spending=-300.0))
    # financing: principal 2000 (out); interest 300 routes to operating
    session.add(LoanJournal(loan_id="LN-1", loan_excute_type="principal", excute_price=2000.0, excute_date="20260315"))
    session.add(LoanJournal(loan_id="LN-1", loan_excute_type="interest", excute_price=300.0, excute_date="20260315"))
    session.commit()

    cf = get_cash_flow(session, "monthly", "202612")
    assert cf.type == "monthly"
    assert [a.key for a in cf.summary.activities] == ["operating", "investing", "financing"]
    acts = {a.key: a for a in cf.summary.activities}
    assert acts["operating"].net == 3200.0  # 5000 - 1000 - 500 - 300
    assert acts["investing"].net == -800.0
    assert acts["financing"].net == -2000.0
    assert cf.summary.net_change == 400.0
    # Per-period: 202603 holds income/expense/interest/principal; 202604 the buy.
    pt = {p.period: p for p in cf.points}
    assert pt["202603"].operating == 3200.0
    assert pt["202603"].financing == -2000.0
    assert pt["202604"].investing == -800.0
    assert round(sum(p.net_change for p in cf.points), 2) == cf.summary.net_change


def test_cash_flow_excludes_transfer_and_handles_borrowing(session: Session) -> None:
    session.add(_expense_journal(vesting_month="202605", spend_date="20260501", action_main_type="Transfer", spending=-9999.0))
    session.add(LoanJournal(loan_id="LN-9", loan_excute_type="increment", excute_price=100000.0, excute_date="20260510"))
    session.add(LoanJournal(loan_id="LN-9", loan_excute_type="principal", excute_price=4000.0, excute_date="20260610"))
    session.commit()

    cf = get_cash_flow(session, "monthly", "202612")
    fin = {a.key: a for a in cf.summary.activities}["financing"]
    assert fin.net == 96000.0  # 100000 borrowed − 4000 repaid
    assert cf.summary.net_change == 96000.0  # transfer contributes nothing


# ---------- Ticket 5: YoY + largest transactions ----------


def test_expense_insights_yoy_and_largest(session: Session) -> None:
    session.add(CodeData(code_id="E01", code_type="Floating", name="餐飲", in_use="Y", code_index=1))
    session.add(CodeData(code_id="F01", code_type="Fixed", name="居住", in_use="Y", code_index=2))
    # 2026: 餐飲 200 (150 + 50), 居住 800
    session.add(_expense_journal(vesting_month="202603", spend_date="20260301", action_main="E01", action_main_type="Floating", spending=-150.0, note="big dinner"))
    session.add(_expense_journal(vesting_month="202604", spend_date="20260401", action_main="E01", action_main_type="Floating", spending=-50.0))
    session.add(_expense_journal(vesting_month="202605", spend_date="20260501", action_main="F01", action_main_type="Fixed", spending=-800.0, note="rent"))
    # 2025: 餐飲 120, 居住 600
    session.add(_expense_journal(vesting_month="202506", spend_date="20250601", action_main="E01", action_main_type="Floating", spending=-120.0))
    session.add(_expense_journal(vesting_month="202507", spend_date="20250701", action_main="F01", action_main_type="Fixed", spending=-600.0))
    session.commit()

    ins = get_expense_insights(session, "2026")
    assert ins.year == "2026"
    yoy = {r.code: r for r in ins.yoy}
    assert yoy["F01"].current == 800.0 and yoy["F01"].previous == 600.0 and yoy["F01"].delta == 200.0
    assert yoy["E01"].current == 200.0 and yoy["E01"].previous == 120.0
    # ordered by |delta| desc → 居住 (200) before 餐飲 (80)
    assert [r.code for r in ins.yoy] == ["F01", "E01"]
    # largest: current-year txns only, by magnitude desc
    assert [t.amount for t in ins.largest] == [800.0, 150.0, 50.0]
    assert ins.largest[0].category == "居住"
    assert ins.largest[0].note == "rent"
