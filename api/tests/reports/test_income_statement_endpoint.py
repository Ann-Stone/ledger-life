"""Comprehensive income statement (綜合損益表) endpoint tests."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.monthly_report.insurance_net_value_history import (
    InsuranceNetValueHistory,
)
from app.models.monthly_report.journal import Journal
from app.models.monthly_report.stock_net_value_history import StockNetValueHistory
from app.models.settings.code_data import CodeData


def _journal(**overrides) -> Journal:
    base = dict(
        vesting_month="202602",
        spend_date="20260210",
        spend_way="A1",
        spend_way_type="account",
        spend_way_table="Account",
        action_main="X01",
        action_main_type="Floating",
        action_main_table="Code_Data",
        spending=-100.0,
    )
    base.update(overrides)
    return Journal(**base)


def _snvh(**overrides) -> StockNetValueHistory:
    base = dict(
        vesting_month="202602",
        id="STK-H-1",
        asset_id="AC-STK-1",
        stock_code="AAPL",
        stock_name="Apple",
        amount=10.0,
        price=0.0,
        cost=0.0,
        fx_code="TWD",
        fx_rate=1.0,
    )
    base.update(overrides)
    return StockNetValueHistory(**base)


def _capital_gain_code() -> CodeData:
    return CodeData(
        code_id="CG", code_type="Invest", name="資本利得", parent_id="INV",
        in_use="Y", code_index=1,
    )


def test_income_statement_three_sections_tie_out(
    client: TestClient, session: Session
) -> None:
    session.add(_capital_gain_code())
    # 本業: active income − fixed − floating
    session.add(_journal(action_main="SAL", action_main_type="Income", spending=80000.0))
    session.add(_journal(action_main="RENT", action_main_type="Fixed", spending=-25000.0))
    session.add(_journal(action_main="FUN", action_main_type="Floating", spending=-18000.0))
    # 投資: 孳息 (passive) + 已實現資本利得 (資本利得 sub) + 未實現 (price − cost)
    session.add(_journal(action_main="DIV", action_main_type="Passive", spending=3000.0))
    session.add(
        _journal(action_main="INV", action_sub="CG", action_main_type="Invest", spending=5000.0)
    )
    session.add(_snvh(price=112000.0, cost=100000.0))  # unrealized = 12000 (no prior snapshot)
    session.commit()

    r = client.get("/reports/income-statement/monthly?vesting_month=202602")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["type"] == "monthly"
    assert len(data["points"]) == 12

    last = data["points"][-1]
    assert last["period"] == "202602"
    assert last["active_income"] == 80000.0
    assert last["fixed"] == 25000.0
    assert last["floating"] == 18000.0
    assert last["operating_net"] == 37000.0  # 80000 - 25000 - 18000
    assert last["dividend"] == 3000.0
    assert last["realized"] == 5000.0
    assert last["unrealized"] == 12000.0
    assert last["investment_net"] == 20000.0  # 3000 + 5000 + 12000
    assert last["comprehensive_net"] == 57000.0  # 37000 + 20000

    s = data["summary"]
    assert s["operating_net"] == 37000.0
    assert s["investment_net"] == 20000.0
    assert s["comprehensive_net"] == 57000.0
    # Section invariants hold across the whole window.
    assert s["operating_net"] == round(s["active_income"] - s["fixed"] - s["floating"], 2)
    assert s["investment_net"] == round(s["dividend"] + s["realized"] + s["unrealized"], 2)
    assert s["comprehensive_net"] == round(s["operating_net"] + s["investment_net"], 2)


def test_loan_interest_lowers_operating_net_not_double_counted(
    client: TestClient, session: Session
) -> None:
    """貸款利息 appears in 本業 (from Loan_Journal) without double-counting.

    The report-neutral LoanRepayment journal is NOT counted as an expense; the
    interest enters operating_net only via Loan_Journal, and principal never
    touches the income statement.
    """
    from app.models.assets.loan import Loan, LoanJournal

    session.add(_journal(action_main="SAL", action_main_type="Income", spending=80000.0))
    # Report-neutral repayment journal (must not show as an expense).
    session.add(
        _journal(
            action_main="LoanRepayment", action_main_type="LoanRepayment",
            action_main_table="Loan", action_sub="LN-1", spending=-9200.0,
        )
    )
    session.add(
        Loan(
            loan_id="LN-1", loan_name="Mortgage", loan_type="mortgage", account_id="A1",
            account_name="Bank", interest_rate=0.035, period=360, apply_date="20200101",
            grace_expire_date=None, pay_day=1, amount=250000.0, repayed=0.0, loan_index=1,
        )
    )
    session.add(LoanJournal(loan_id="LN-1", loan_excute_type="interest", excute_price=1200.0, excute_date="20260210"))
    session.add(LoanJournal(loan_id="LN-1", loan_excute_type="principal", excute_price=8000.0, excute_date="20260210"))
    session.commit()

    r = client.get("/reports/income-statement/monthly?vesting_month=202602")
    assert r.status_code == 200
    last = r.json()["data"]["points"][-1]
    assert last["loan_interest"] == 1200.0
    assert last["fixed"] == 0.0 and last["floating"] == 0.0  # repayment not an expense
    assert last["operating_net"] == 78800.0  # 80000 − 0 − 0 − 1200 (principal excluded)

    s = r.json()["data"]["summary"]
    assert s["loan_interest"] == 1200.0
    assert s["operating_net"] == round(
        s["active_income"] - s["fixed"] - s["floating"] - s["loan_interest"], 2
    )


def test_capital_gain_not_double_counted_even_if_mistyped(
    client: TestClient, session: Session
) -> None:
    """A 資本利得 row is pulled out by *name* before income netting, so even a
    mis-typed (Income) capital-gain row lands only in realized, never in income."""
    session.add(
        CodeData(code_id="CG", code_type="Income", name="資本利得", parent_id=None,
                 in_use="Y", code_index=1)
    )
    session.add(_journal(action_main="SAL", action_main_type="Income", spending=80000.0))
    # Mis-typed as Income but its category name is 資本利得.
    session.add(_journal(action_main="CG", action_main_type="Income", spending=9999.0))
    session.commit()

    r = client.get("/reports/income-statement/monthly?vesting_month=202602")
    data = r.json()["data"]
    s = data["summary"]
    assert s["active_income"] == 80000.0  # 9999 NOT folded into 本業收入
    assert s["realized"] == 9999.0


def test_passive_income_is_dividend_not_active(
    client: TestClient, session: Session
) -> None:
    session.add(_journal(action_main="DIV", action_main_type="Passive", spending=3000.0))
    session.commit()

    r = client.get("/reports/income-statement/monthly?vesting_month=202602")
    s = r.json()["data"]["summary"]
    assert s["active_income"] == 0.0
    assert s["dividend"] == 3000.0
    assert s["operating_net"] == 0.0
    assert s["investment_net"] == 3000.0


def test_unrealized_is_period_change(client: TestClient, session: Session) -> None:
    # Two in-window monthly snapshots: U(202601)=20000, U(202602)=50000.
    session.add(_snvh(vesting_month="202601", price=100000.0, cost=80000.0))
    session.add(_snvh(vesting_month="202602", price=130000.0, cost=80000.0))
    session.commit()

    r = client.get("/reports/income-statement/monthly?vesting_month=202602")
    points = r.json()["data"]["points"]
    by_period = {p["period"]: p for p in points}
    assert by_period["202601"]["unrealized"] == 20000.0  # first appearance
    assert by_period["202602"]["unrealized"] == 30000.0  # 50000 - 20000
    # Summary unrealized telescopes to U(last) − U(base).
    assert r.json()["data"]["summary"]["unrealized"] == 50000.0


def test_unrealized_includes_insurance_surrender_growth(
    client: TestClient, session: Session
) -> None:
    """Insurance cash-value growth (surrender_value − cost) flows into unrealized."""
    session.add(
        InsuranceNetValueHistory(
            vesting_month="202602", id="INS-1", asset_id="AC-INS", name="Whole life",
            surrender_value=130000.0, cost=100000.0, fx_code="TWD", fx_rate=1.0,
        )
    )
    session.commit()

    r = client.get("/reports/income-statement/monthly?vesting_month=202602")
    by_period = {p["period"]: p for p in r.json()["data"]["points"]}
    assert by_period["202602"]["unrealized"] == 30000.0  # 130000 - 100000
    assert r.json()["data"]["summary"]["unrealized"] == 30000.0


def test_income_statement_invalid_type_returns_422(client: TestClient) -> None:
    r = client.get("/reports/income-statement/weekly?vesting_month=202412")
    assert r.status_code == 422


def test_income_statement_invalid_month_returns_422(client: TestClient) -> None:
    r = client.get("/reports/income-statement/monthly?vesting_month=2024")
    assert r.status_code == 422
