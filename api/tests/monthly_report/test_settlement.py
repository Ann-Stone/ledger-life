"""BE-019 — Monthly balance settlement tests."""
from __future__ import annotations

import json
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

import app.models  # noqa: F401  registers tables
from app.database import get_session
from app.main import app
from app.models.assets.estate import Estate, EstateJournal
from app.models.assets.insurance import Insurance, InsuranceJournal
from app.models.assets.loan import Loan, LoanJournal
from app.models.assets.stock import StockDetail, StockJournal
from app.models.dashboard.fx_rate import FXRate
from app.models.dashboard.stock_price_history import StockPriceHistory
from app.models.monthly_report.account_balance import AccountBalance
from app.models.monthly_report.credit_card_balance import CreditCardBalance
from app.models.monthly_report.estate_net_value_history import EstateNetValueHistory
from app.models.monthly_report.insurance_net_value_history import (
    InsuranceNetValueHistory,
)
from app.models.monthly_report.journal import Journal
from app.models.monthly_report.loan_balance import LoanBalance
from app.models.monthly_report.settlement import SettlementResult
from app.models.monthly_report.stock_net_value_history import StockNetValueHistory
from app.models.settings.account import Account
from app.models.settings.credit_card import CreditCard
from app.services import settlement_service
from app.services.settlement_service import (
    query_has_record_flags,
    run_account_balance_step,
    run_credit_card_balance_step,
    run_estate_step,
    run_insurance_step,
    run_loan_step,
    run_stock_step,
    settle,
)
from app.services.fx_lookup import fx_rate_for_month

GOLDEN_PATH = Path(__file__).resolve().parent.parent / "fixtures" / "settlement_golden.json"
VM = "202603"


def _seed(session: Session) -> None:
    """Populate a fresh session with the BE-019 settlement fixture state."""
    # Accounts: TWD base + USD foreign + finance/normal pair for FX branches.
    session.add(
        Account(
            account_id="TWD-1", name="TWD Bank", account_type="bank",
            fx_code="TWD", is_calculate="Y", in_use="Y",
            discount=1.0, owner="stone", account_index=1,
        )
    )
    session.add(
        Account(
            account_id="USD-1", name="USD Bank", account_type="bank",
            fx_code="USD", is_calculate="Y", in_use="Y",
            discount=1.0, owner="stone", account_index=2,
        )
    )
    session.add(
        Account(
            account_id="FIN-1", name="Finance Acct", account_type="finance",
            fx_code="TWD", is_calculate="Y", in_use="Y",
            discount=1.0, owner="stone", account_index=3,
        )
    )
    session.add(
        Account(
            account_id="JPY-1", name="JPY Bank", account_type="bank",
            fx_code="JPY", is_calculate="Y", in_use="Y",
            discount=1.0, owner="stone", account_index=4,
        )
    )
    # Credit cards
    session.add(CreditCard(credit_card_id="CC-A", card_name="Card A", fx_code="TWD", in_use="Y", credit_card_index=1))
    session.add(CreditCard(credit_card_id="CC-B", card_name="Card B", fx_code="USD", in_use="Y", credit_card_index=2))

    # FX rates (March 2026)
    session.add(FXRate(import_date="20260331", code="USD", buy_rate=32.0))
    session.add(FXRate(import_date="20260331", code="JPY", buy_rate=0.22))

    # Estate + journal (purchase 500,000 TWD)
    session.add(
        Estate(
            estate_id="EST-1", estate_name="Condo", estate_type="residential",
            estate_address="X", asset_id="AC-REAL", obtain_date="20200101",
            estate_status="hold",
        )
    )
    session.add(
        EstateJournal(
            estate_id="EST-1", estate_excute_type="purchase",
            excute_price=500000.0, excute_date="20200115",
        )
    )

    # Insurance: USD policy, 2 'pay' (扣款) journals (1200 each = 2400 cost)
    session.add(
        Insurance(
            insurance_id="INS-1", insurance_name="Whole life", asset_id="AC-INS",
            in_account="USD-1", out_account="USD-1", start_date="20200101",
            end_date="20500101", pay_type="annual", pay_day="01/15",
            expected_spend=1200.0, has_closed="N",
        )
    )
    session.add(
        InsuranceJournal(
            insurance_id="INS-1", insurance_excute_type="pay",
            excute_price=1200.0, excute_date="20250115",
        )
    )
    session.add(
        InsuranceJournal(
            insurance_id="INS-1", insurance_excute_type="pay",
            excute_price=1200.0, excute_date="20260115",
        )
    )

    # Loan
    session.add(
        Loan(
            loan_id="LN-1", loan_name="Mortgage", loan_type="mortgage",
            account_id="TWD-1", account_name="TWD Bank",
            interest_rate=0.035, period=360, apply_date="20200101",
            grace_expire_date=None, pay_day=1, amount=250000.0,
            repayed=10000.0, loan_index=1,
        )
    )
    session.add(
        LoanJournal(loan_id="LN-1", loan_excute_type="principal", excute_price=10000.0, excute_date="20260301")
    )
    session.add(
        LoanJournal(loan_id="LN-1", loan_excute_type="interest", excute_price=500.0, excute_date="20260301")
    )

    # Stocks: AAPL (net 10), GOOG (net 0 → skipped)
    session.add(StockJournal(stock_id="H1", stock_code="AAPL", stock_name="Apple", asset_id="AC-STK", expected_spend=0.0))
    session.add(StockJournal(stock_id="H2", stock_code="GOOG", stock_name="Google", asset_id="AC-STK", expected_spend=0.0))
    # excute_price is the whole-transaction amount (fees included), not per-share:
    # AAPL bought for 1800 → cost 1800; GOOG bought 700, sold 725, nets to 0 shares.
    session.add(
        StockDetail(
            stock_id="H1", excute_type="buy", excute_amount=10.0, excute_price=1800.0,
            excute_date="20260201", account_id="USD-1", account_name="USD Bank",
        )
    )
    session.add(
        StockDetail(
            stock_id="H2", excute_type="buy", excute_amount=5.0, excute_price=700.0,
            excute_date="20260201", account_id="USD-1", account_name="USD Bank",
        )
    )
    session.add(
        StockDetail(
            stock_id="H2", excute_type="sell", excute_amount=-5.0, excute_price=725.0,
            excute_date="20260220", account_id="USD-1", account_name="USD Bank",
        )
    )
    session.add(StockPriceHistory(stock_code="AAPL", fetch_date="20260331", open_price=200.0, highest_price=210.0, lowest_price=195.0, close_price=205.0))

    # Journal entries for March
    journals = [
        Journal(
            vesting_month=VM, spend_date="20260305", spend_way="TWD-1",
            spend_way_type="account", spend_way_table="Account",
            action_main="EXP01", action_main_type="expense",
            action_main_table="Code_Data", spending=-1500.0, note=None,
        ),
        Journal(
            vesting_month=VM, spend_date="20260310", spend_way="USD-1",
            spend_way_type="account", spend_way_table="Account",
            action_main="EXP02", action_main_type="expense",
            action_main_table="Code_Data", spending=-50.0, note=None,
        ),
        Journal(
            vesting_month=VM, spend_date="20260312", spend_way="CC-A",
            spend_way_type="credit_card", spend_way_table="Credit_Card",
            action_main="EXP01", action_main_type="expense",
            action_main_table="Code_Data", spending=-300.0, note=None,
        ),
        Journal(
            vesting_month=VM, spend_date="20260318", spend_way="CC-B",
            spend_way_type="credit_card", spend_way_table="Credit_Card",
            action_main="EXP01", action_main_type="expense",
            action_main_table="Code_Data", spending=-20.0, note=None,
        ),
        # Stock buy through Account → triggers stock-flag in has-record query
        Journal(
            vesting_month=VM, spend_date="20260315", spend_way="USD-1",
            spend_way_type="account", spend_way_table="Account",
            action_main="STK-AAPL", action_main_type="invest",
            action_main_table="Stock", action_sub="STK-AAPL",
            action_sub_type="stock", action_sub_table="Stock",
            spending=-1800.0, note=None,
        ),
        # Loan repayment (principal)
        Journal(
            vesting_month=VM, spend_date="20260301", spend_way="TWD-1",
            spend_way_type="account", spend_way_table="Account",
            action_main="LN-1", action_main_type="liability",
            action_main_table="Loan", action_sub="LN-1",
            action_sub_type="loan", action_sub_table="Loan",
            spending=-10500.0, note=None,
        ),
        # Insurance premium
        Journal(
            vesting_month=VM, spend_date="20260115", spend_way="USD-1",
            spend_way_type="account", spend_way_table="Account",
            action_main="INS-1", action_main_type="insurance",
            action_main_table="Insurance", action_sub="INS-1",
            action_sub_type="insurance", action_sub_table="Insurance",
            spending=-1200.0, note=None,
        ),
        # Estate repaint
        Journal(
            vesting_month=VM, spend_date="20260320", spend_way="TWD-1",
            spend_way_type="account", spend_way_table="Account",
            action_main="EST-1", action_main_type="estate",
            action_main_table="Estate", action_sub="EST-1",
            action_sub_type="estate", action_sub_table="Estate",
            spending=-2000.0, note=None,
        ),
    ]
    for j in journals:
        session.add(j)
    session.commit()


@pytest.fixture
def settlement_fixture_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        _seed(s)
        yield s


@pytest.fixture
def settlement_client(
    settlement_fixture_session: Session,
) -> Generator[TestClient, None, None]:
    def _override():
        yield settlement_fixture_session

    app.dependency_overrides[get_session] = _override
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(get_session, None)


# ---- 1: schema ----


def test_settlement_result_schema() -> None:
    js = SettlementResult.model_json_schema()
    assert "example" in js
    for n, p in js["properties"].items():
        assert "description" in p, n
        assert "examples" in p, n


# ---- 2-3: helpers ----


def test_has_record_flags(settlement_fixture_session: Session) -> None:
    flags = query_has_record_flags(settlement_fixture_session, VM)
    assert flags == {
        "estate": True,
        "insurance": True,
        "loan": True,
        "stock": True,
    }


def test_fx_rate_lookup_fallback(settlement_fixture_session: Session) -> None:
    s = settlement_fixture_session
    assert fx_rate_for_month(s, "TWD", VM, on_missing="raise") == 1.0
    assert fx_rate_for_month(s, "USD", VM, on_missing="raise") == 32.0
    # Future month — fallback to most recent prior row.
    assert fx_rate_for_month(s, "USD", "202612", on_missing="raise") == 32.0
    with pytest.raises(ValueError):
        fx_rate_for_month(s, "EUR", VM, on_missing="raise")


# ---- 4-7: per-step ----


def test_run_estate_step(settlement_fixture_session: Session) -> None:
    n = run_estate_step(settlement_fixture_session, VM)
    settlement_fixture_session.commit()
    assert n == 1
    rows = settlement_fixture_session.exec(select(EstateNetValueHistory)).all()
    assert len(rows) == 1
    assert rows[0].cost == 500000.0
    # TWD estate (no fx_code set → defaults TWD), base-currency rate.
    assert rows[0].fx_code == "TWD"
    assert rows[0].fx_rate == 1.0


def test_run_insurance_step(settlement_fixture_session: Session) -> None:
    n = run_insurance_step(settlement_fixture_session, VM)
    settlement_fixture_session.commit()
    assert n == 1
    row = settlement_fixture_session.exec(select(InsuranceNetValueHistory)).first()
    assert row.cost == 2400.0
    assert row.fx_code == "USD"
    assert row.fx_rate == 32.0


def test_run_loan_step(settlement_fixture_session: Session) -> None:
    n = run_loan_step(settlement_fixture_session, VM)
    settlement_fixture_session.commit()
    assert n == 1
    row = settlement_fixture_session.exec(select(LoanBalance)).first()
    assert row.balance == 240000.0
    assert row.cost == 500.0
    # Repayment account TWD-1 → base currency.
    assert row.fx_code == "TWD"
    assert row.fx_rate == 1.0


def test_run_estate_and_loan_step_foreign_currency(
    settlement_fixture_session: Session,
) -> None:
    s = settlement_fixture_session
    # Overseas property in USD (estate carries its own currency).
    s.add(
        Estate(
            estate_id="EST-USD", estate_name="Overseas Condo", estate_type="residential",
            estate_address="Y", asset_id="AC-REAL", obtain_date="20210101",
            estate_status="hold", fx_code="USD",
        )
    )
    s.add(
        EstateJournal(
            estate_id="EST-USD", estate_excute_type="purchase",
            excute_price=300000.0, excute_date="20210115",
        )
    )
    # Foreign loan: currency follows the USD repayment account.
    s.add(
        Loan(
            loan_id="LN-USD", loan_name="US Mortgage", loan_type="mortgage",
            account_id="USD-1", account_name="USD Bank", interest_rate=0.04,
            period=360, apply_date="20210101", grace_expire_date=None,
            pay_day=1, amount=100000.0, repayed=0.0, loan_index=2,
        )
    )
    s.commit()

    run_estate_step(s, VM)
    run_loan_step(s, VM)
    s.commit()

    est = s.exec(
        select(EstateNetValueHistory).where(EstateNetValueHistory.id == "EST-USD")
    ).first()
    assert est.fx_code == "USD"
    assert est.fx_rate == 32.0
    loan = s.exec(select(LoanBalance).where(LoanBalance.id == "LN-USD")).first()
    assert loan.fx_code == "USD"
    assert loan.fx_rate == 32.0


def test_run_stock_step_zero_amount_skipped(
    settlement_fixture_session: Session,
) -> None:
    n = run_stock_step(settlement_fixture_session, VM)
    settlement_fixture_session.commit()
    assert n == 1
    rows = settlement_fixture_session.exec(select(StockNetValueHistory)).all()
    codes = {r.stock_code for r in rows}
    assert codes == {"AAPL"}
    aapl = rows[0]
    # market value = close (205) * amount (10) = 2050
    assert aapl.amount == 10.0
    assert aapl.price == 2050.0
    assert aapl.cost == 1800.0
    assert aapl.fx_code == "USD"


def test_run_stock_step_ignores_cash_dividend(
    settlement_fixture_session: Session,
) -> None:
    """A synced cash-dividend row must not inflate settled shares/cost.

    Net worth comes from the Journal ledger plus the buy/sell/stock rows; the
    dividend's cash inflow is already booked in its Passive Journal entry, so
    run_stock_step deliberately skips 'cash' rows. Regression guard for the
    月度帳務 → Stock_Detail dividend sync (no double-count in net worth).
    """
    s = settlement_fixture_session
    s.add(
        StockDetail(
            stock_id="H1", excute_type="cash", excute_amount=0.0, excute_price=120.0,
            excute_date="20260315", account_id="USD-1", account_name="USD Bank",
        )
    )
    s.commit()
    run_stock_step(s, VM)
    s.commit()
    aapl = s.exec(
        select(StockNetValueHistory).where(StockNetValueHistory.stock_code == "AAPL")
    ).first()
    # Identical to the no-dividend baseline above: the cash row contributes nothing.
    assert aapl.amount == 10.0
    assert aapl.price == 2050.0
    assert aapl.cost == 1800.0


# ---- 8-9: balance steps ----


def test_run_account_balance_cascade_clear(
    settlement_fixture_session: Session,
) -> None:
    s = settlement_fixture_session
    s.add(AccountBalance(vesting_month="202604", id="TWD-1", name="TWD Bank", balance=999.0, fx_code="TWD", fx_rate=1.0, is_calculate="Y"))
    s.commit()
    run_account_balance_step(s, VM)
    s.commit()
    later = s.exec(select(AccountBalance).where(AccountBalance.vesting_month == "202604")).all()
    assert later == []
    rows = s.exec(select(AccountBalance).where(AccountBalance.vesting_month == VM)).all()
    assert {r.id for r in rows} == {"TWD-1", "USD-1", "FIN-1", "JPY-1"}


def test_run_credit_card_balance_cascade_clear(
    settlement_fixture_session: Session,
) -> None:
    s = settlement_fixture_session
    s.add(CreditCardBalance(vesting_month="202604", id="CC-A", name="Card A", balance=42.0, fx_rate=1.0))
    s.commit()
    run_credit_card_balance_step(s, VM)
    s.commit()
    later = s.exec(select(CreditCardBalance).where(CreditCardBalance.vesting_month == "202604")).all()
    assert later == []
    rows = s.exec(select(CreditCardBalance).where(CreditCardBalance.vesting_month == VM)).all()
    assert {r.id for r in rows} == {"CC-A", "CC-B"}


# ---- 10: rollback ----


def test_settle_transaction_rollback_on_failure(
    settlement_fixture_session: Session, monkeypatch: pytest.MonkeyPatch,
) -> None:
    s = settlement_fixture_session

    def _boom(*_a, **_kw):
        raise RuntimeError("forced failure")

    monkeypatch.setattr(settlement_service, "select_month_close_price", _boom)
    with pytest.raises(RuntimeError):
        settle(s, VM)

    assert s.exec(select(StockNetValueHistory)).all() == []
    assert s.exec(select(EstateNetValueHistory)).all() == []
    assert s.exec(select(InsuranceNetValueHistory)).all() == []
    assert s.exec(select(LoanBalance)).all() == []
    assert s.exec(select(AccountBalance)).all() == []
    assert s.exec(select(CreditCardBalance)).all() == []


# ---- 11: endpoint ----


def test_put_settle_endpoint(settlement_client: TestClient) -> None:
    r = settlement_client.put(f"/monthly-report/balance/{VM}/settle")
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["vesting_month"] == VM
    assert data["estate_rows"] == 1
    assert data["insurance_rows"] == 1
    assert data["loan_rows"] == 1
    assert data["stock_rows"] == 1
    assert data["account_rows"] == 4
    assert data["credit_card_rows"] == 2


# ---- 12: router mounted ----


def test_balance_router_mounted() -> None:
    # Use FastAPI's own resolved schema paths rather than walking app.routes:
    # the internal route-tree structure changed across starlette versions, but
    # openapi()["paths"] is the stable, version-agnostic view of mounted paths.
    paths = set(app.openapi()["paths"])
    assert "/monthly-report/balance/{vesting_month}/settle" in paths


# ---- 13: fixture loads ----


def test_settlement_fixture_loads(settlement_fixture_session: Session) -> None:
    j = settlement_fixture_session.exec(select(Journal)).all()
    assert len(j) >= 8


# ---- 14: golden ----


def _to_jsonable(rows: list, key_fields: list[str], value_fields: list[str]) -> list[dict]:
    out = []
    for r in rows:
        d = {f: getattr(r, f) for f in key_fields + value_fields}
        out.append(d)
    return sorted(out, key=lambda d: tuple(d[f] for f in key_fields))


def test_settle_golden_month(settlement_fixture_session: Session) -> None:
    s = settlement_fixture_session
    settle(s, VM)
    actual = {
        "estate": _to_jsonable(
            s.exec(select(EstateNetValueHistory)).all(),
            ["id"], ["asset_id", "name", "market_value", "cost", "estate_status"],
        ),
        "insurance": _to_jsonable(
            s.exec(select(InsuranceNetValueHistory)).all(),
            ["id"], ["asset_id", "name", "surrender_value", "cost", "fx_code", "fx_rate"],
        ),
        "loan": _to_jsonable(
            s.exec(select(LoanBalance)).all(),
            ["id"], ["name", "balance", "cost"],
        ),
        "stock": _to_jsonable(
            s.exec(select(StockNetValueHistory)).all(),
            ["id"], ["asset_id", "stock_code", "stock_name", "amount", "price", "cost", "fx_code", "fx_rate"],
        ),
        "account_balance": _to_jsonable(
            s.exec(select(AccountBalance)).all(),
            ["id"], ["name", "balance", "fx_code", "fx_rate", "is_calculate"],
        ),
        "credit_card_balance": _to_jsonable(
            s.exec(select(CreditCardBalance)).all(),
            ["id"], ["name", "balance", "fx_rate"],
        ),
    }
    expected = json.loads(GOLDEN_PATH.read_text())
    assert actual == expected


# ---- 15: idempotency ----


def test_settle_idempotent(settlement_fixture_session: Session) -> None:
    s = settlement_fixture_session
    settle(s, VM)
    snap1 = {
        "estate": [r.model_dump() for r in s.exec(select(EstateNetValueHistory)).all()],
        "insurance": [r.model_dump() for r in s.exec(select(InsuranceNetValueHistory)).all()],
        "loan": [r.model_dump() for r in s.exec(select(LoanBalance)).all()],
        "stock": [r.model_dump() for r in s.exec(select(StockNetValueHistory)).all()],
        "account": [r.model_dump() for r in s.exec(select(AccountBalance)).all()],
        "credit_card": [r.model_dump() for r in s.exec(select(CreditCardBalance)).all()],
    }
    settle(s, VM)
    snap2 = {
        "estate": [r.model_dump() for r in s.exec(select(EstateNetValueHistory)).all()],
        "insurance": [r.model_dump() for r in s.exec(select(InsuranceNetValueHistory)).all()],
        "loan": [r.model_dump() for r in s.exec(select(LoanBalance)).all()],
        "stock": [r.model_dump() for r in s.exec(select(StockNetValueHistory)).all()],
        "account": [r.model_dump() for r in s.exec(select(AccountBalance)).all()],
        "credit_card": [r.model_dump() for r in s.exec(select(CreditCardBalance)).all()],
    }
    assert snap1 == snap2


# ---- 16: cascade invalidation ----


def test_settle_cascades_invalidation_to_later_months(
    settlement_fixture_session: Session,
) -> None:
    s = settlement_fixture_session
    settle(s, VM)
    # Settle 202604 with no journals — just carry-forward.
    settle(s, "202604")
    # Mutate a 202603 journal.
    j = s.exec(select(Journal).where(Journal.vesting_month == VM)).first()
    j.spending = j.spending - 100
    s.add(j)
    s.commit()
    settle(s, VM)
    later_acct = s.exec(
        select(AccountBalance).where(AccountBalance.vesting_month == "202604")
    ).all()
    later_cc = s.exec(
        select(CreditCardBalance).where(CreditCardBalance.vesting_month == "202604")
    ).all()
    assert later_acct == []
    assert later_cc == []


# ---- 17: rollback via endpoint ----


def test_settle_rolls_back_on_stock_step_failure(
    settlement_fixture_session: Session, monkeypatch: pytest.MonkeyPatch,
) -> None:
    s = settlement_fixture_session

    def _boom(*_a, **_kw):
        raise RuntimeError("forced failure")

    monkeypatch.setattr(settlement_service, "select_month_close_price", _boom)
    with pytest.raises(RuntimeError):
        settle(s, VM)

    assert s.exec(select(StockNetValueHistory)).all() == []
    assert s.exec(select(EstateNetValueHistory)).all() == []
    assert s.exec(select(InsuranceNetValueHistory)).all() == []
    assert s.exec(select(LoanBalance)).all() == []
