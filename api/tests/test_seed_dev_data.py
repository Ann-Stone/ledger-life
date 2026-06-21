"""Acceptance tests for ``scripts.seed_dev_data`` (BE-B04).

Every test points at a throw-away SQLite under ``tmp_path``; the user's
real ``~/.networth/networth.db`` is never opened.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from sqlmodel import Session, func, select

from app.models.assets.estate import Estate, EstateJournal
from app.models.assets.insurance import Insurance, InsuranceJournal
from app.models.assets.loan import Loan, LoanJournal
from app.models.assets.other_asset import OtherAsset
from app.models.assets.stock import StockDetail, StockJournal
from app.models.dashboard.fx_rate import FXRate
from app.models.dashboard.stock_price_history import StockPriceHistory
from app.models.dashboard.target_setting import TargetSetting
from app.models.monthly_report.account_balance import AccountBalance
from app.models.monthly_report.credit_card_balance import CreditCardBalance
from app.models.monthly_report.estate_net_value_history import EstateNetValueHistory
from app.models.monthly_report.insurance_net_value_history import (
    InsuranceNetValueHistory,
)
from app.models.monthly_report.journal import Journal
from app.models.monthly_report.stock_net_value_history import StockNetValueHistory
from app.models.settings.account import Account
from app.models.settings.alarm import Alarm
from app.models.settings.budget import Budget
from app.models.settings.code_data import CodeData
from app.models.settings.credit_card import CreditCard
from scripts import seed_dev_data


# ---------------------------------------------------------------------------
# Shared helpers / fixtures
# ---------------------------------------------------------------------------

def _tmp_url(tmp_path: Path) -> str:
    return f"sqlite:///{tmp_path / 'seed_test.db'}"


@pytest.fixture
def seeded_engine(tmp_path):
    url = _tmp_url(tmp_path)
    counts = seed_dev_data.main(target_db_url=url, wipe=True)
    engine = seed_dev_data._build_engine(url)
    yield engine, counts
    engine.dispose()


def _scalar(value) -> int:
    if isinstance(value, tuple):
        return int(value[0])
    return int(value)


# ---------------------------------------------------------------------------
# Sub-task 1 — script importable / CLI parser builds
# ---------------------------------------------------------------------------

def test_cli_parser_help_runs():
    parser = seed_dev_data._build_arg_parser()
    # parse_args with --help would exit; instead verify the arguments exist.
    actions = {a.dest for a in parser._actions}
    assert "target_db_url" in actions
    assert "wipe" in actions


# ---------------------------------------------------------------------------
# Sub-task 2 — dev-guard
# ---------------------------------------------------------------------------

def test_dev_guard_rejects_prod_url():
    with pytest.raises(RuntimeError):
        seed_dev_data._assert_dev_db("postgres://localhost/db")
    with pytest.raises(RuntimeError):
        seed_dev_data._assert_dev_db("sqlite:///./networth_prod.db")
    with pytest.raises(RuntimeError):
        seed_dev_data._assert_dev_db("mysql://user@host/db")


def test_dev_guard_accepts_dev_paths(tmp_path):
    # tmp paths ending in seed_test.db are accepted.
    seed_dev_data._assert_dev_db(f"sqlite:///{tmp_path / 'seed_test.db'}")
    seed_dev_data._assert_dev_db(f"sqlite:///{tmp_path / 'foo_dev.db'}")
    seed_dev_data._assert_dev_db(f"sqlite:///{tmp_path / 'bar_test.db'}")
    seed_dev_data._assert_dev_db("sqlite:///:memory:")


def test_dev_guard_rejects_unknown_filename(tmp_path):
    with pytest.raises(RuntimeError):
        seed_dev_data._assert_dev_db(f"sqlite:///{tmp_path / 'random.db'}")


# ---------------------------------------------------------------------------
# Sub-task 3 + 20 — wipe / idempotency
# ---------------------------------------------------------------------------

def test_seed_is_idempotent(tmp_path):
    url = _tmp_url(tmp_path)
    counts1 = seed_dev_data.main(target_db_url=url, wipe=True)
    counts2 = seed_dev_data.main(target_db_url=url, wipe=True)
    assert counts1 == counts2
    assert all(v > 0 for v in counts1.values())


# ---------------------------------------------------------------------------
# Sub-task 4 — accounts
# ---------------------------------------------------------------------------

def test_accounts_seeded(seeded_engine):
    engine, _ = seeded_engine
    with Session(engine) as s:
        rows = s.exec(select(Account)).all()
    ids = {r.account_id for r in rows}
    assert {"BANK-CASH-01", "BANK-CHASE-01", "INVEST-IB-01", "BANK-CTBC-01"} <= ids
    cash = next(r for r in rows if r.account_id == "BANK-CASH-01")
    assert cash.fx_code == "TWD"
    assert cash.is_calculate == "Y"
    chase = next(r for r in rows if r.account_id == "BANK-CHASE-01")
    assert chase.fx_code == "USD"
    assert chase.discount == 1.0
    assert chase.owner == "stone"
    invest = next(r for r in rows if r.account_id == "INVEST-IB-01")
    assert invest.fx_code == "USD"
    ctbc = next(r for r in rows if r.account_id == "BANK-CTBC-01")
    assert ctbc.in_use == "N"
    indices = {r.account_index for r in rows}
    assert len(indices) == len(rows)  # all populated, all distinct


# ---------------------------------------------------------------------------
# Sub-task 5 — codes covering every code_type
# ---------------------------------------------------------------------------

def test_codes_cover_all_types(seeded_engine):
    engine, _ = seeded_engine
    with Session(engine) as s:
        mains = s.exec(select(CodeData).where(CodeData.parent_id.is_(None))).all()
        subs = s.exec(select(CodeData).where(CodeData.parent_id.is_not(None))).all()
    main_types = {m.code_type for m in mains}
    assert main_types == {"Floating", "Fixed", "Invest", "Income", "Transfer"}
    # Each main has exactly 2 sub-codes via parent_id.
    by_parent: dict[str, list[CodeData]] = {}
    for sub in subs:
        by_parent.setdefault(sub.parent_id, []).append(sub)
    for m in mains:
        assert len(by_parent.get(m.code_id, [])) == 2


# ---------------------------------------------------------------------------
# Sub-task 6 — credit cards
# ---------------------------------------------------------------------------

def test_credit_cards_seeded(seeded_engine):
    engine, _ = seeded_engine
    with Session(engine) as s:
        rows = s.exec(select(CreditCard)).all()
    ids = {r.credit_card_id for r in rows}
    assert {"CC-VISA-01", "CC-MASTER-01", "CC-AMEX-01"} <= ids
    for r in rows:
        # Every column the FE-036 dialog displays has a value.
        assert r.last_day is not None
        assert r.charge_day is not None
        assert r.limit_date is not None
        assert r.feedback_way is not None
        assert r.note is not None


# ---------------------------------------------------------------------------
# Sub-task 7 — budgets across two years
# ---------------------------------------------------------------------------

def test_budgets_two_years(seeded_engine):
    engine, _ = seeded_engine
    with Session(engine) as s:
        rows = s.exec(select(Budget)).all()
    years = {r.budget_year for r in rows}
    assert len(years) == 2
    for r in rows:
        for m in range(1, 13):
            value = getattr(r, f"expected{m:02d}")
            assert value > 0


# ---------------------------------------------------------------------------
# Sub-task 8 — alarms
# ---------------------------------------------------------------------------

def test_alarms_seeded(seeded_engine):
    engine, _ = seeded_engine
    with Session(engine) as s:
        rows = s.exec(select(Alarm)).all()
    types = {r.alarm_type for r in rows}
    assert {"保單續期", "信用卡帳單", "房屋稅", "健檢", "訂閱續訂"} <= types
    with_due = [r for r in rows if r.due_date is not None]
    assert len(with_due) >= 2
    for r in rows:
        assert len(r.alarm_date) == 8 and r.alarm_date.isdigit()


# ---------------------------------------------------------------------------
# Sub-task 9 — journals + polymorphic FK matrix
# ---------------------------------------------------------------------------

def test_journal_polymorphic_fks_consistent(seeded_engine):
    engine, _ = seeded_engine
    with Session(engine) as s:
        rows = s.exec(select(Journal)).all()
        accounts = {a.account_id for a in s.exec(select(Account)).all()}
        cards = {c.credit_card_id for c in s.exec(select(CreditCard)).all()}
        codes = {c.code_id for c in s.exec(select(CodeData)).all()}
    assert len(rows) >= 30
    main_types = {r.action_main_type for r in rows}
    assert {"Floating", "Fixed", "Income", "Invest", "Transfer"} <= main_types
    invoiced = [r for r in rows if r.invoice_number]
    assert len(invoiced) >= 2
    sub_populated = [
        r for r in rows
        if r.action_sub is not None
        and r.action_sub_type is not None
        and r.action_sub_table is not None
    ]
    assert len(sub_populated) >= 5
    months = {r.vesting_month[:6] for r in rows}
    assert len(months) >= 12  # spread across many months in last 24
    for r in rows:
        # spend_way matrix
        if r.spend_way_type == "account":
            assert r.spend_way_table == "Account"
            assert r.spend_way in accounts
        elif r.spend_way_type == "credit_card":
            assert r.spend_way_table == "Credit_Card"
            assert r.spend_way in cards
        else:
            pytest.fail(f"unexpected spend_way_type: {r.spend_way_type}")
        # action_main always Code_Data
        assert r.action_main_table == "Code_Data"
        assert r.action_main in codes
        # action_sub matrix: all-three or none
        triples = (r.action_sub, r.action_sub_type, r.action_sub_table)
        if any(v is not None for v in triples):
            assert all(v is not None for v in triples)
            assert r.action_sub in codes
            assert r.action_sub_table == "Code_Data"


# ---------------------------------------------------------------------------
# Sub-task 10 — settled-month coverage (13 consecutive months for dashboard trend)
# ---------------------------------------------------------------------------

def test_settled_month_thirteen_consecutive(seeded_engine):
    engine, _ = seeded_engine
    with Session(engine) as s:
        ab_months = {
            r.vesting_month for r in s.exec(select(AccountBalance)).all()
        }
        cb_months = {
            r.vesting_month for r in s.exec(select(CreditCardBalance)).all()
        }
        nv_count = _scalar(
            s.exec(select(func.count()).select_from(StockNetValueHistory)).one()
        )
    assert len(ab_months) == 13
    assert len(cb_months) == 13
    assert ab_months == cb_months  # account + card snapshots share the same period set
    # 13 settled stock snapshots (STK-H-SETTLED) plus the 12-row year-report set
    assert nv_count >= 13


# ---------------------------------------------------------------------------
# Sub-task 11 — stock price history
# ---------------------------------------------------------------------------

def test_stock_price_history_seeded(seeded_engine):
    engine, _ = seeded_engine
    with Session(engine) as s:
        rows = s.exec(select(StockPriceHistory)).all()
    by_code: dict[str, int] = {}
    for r in rows:
        by_code[r.stock_code] = by_code.get(r.stock_code, 0) + 1
    assert "2330.TW" in by_code
    assert "AAPL" in by_code
    assert by_code["2330.TW"] >= 6
    assert by_code["AAPL"] >= 6


# ---------------------------------------------------------------------------
# Sub-task 12 — three years of monthly history across categories
# ---------------------------------------------------------------------------

def test_year_report_history_three_years(seeded_engine):
    engine, _ = seeded_engine
    with Session(engine) as s:
        stock = s.exec(select(StockNetValueHistory)).all()
        estate = s.exec(select(EstateNetValueHistory)).all()
        insurance = s.exec(select(InsuranceNetValueHistory)).all()
    total = len(stock) + len(estate) + len(insurance)
    assert total >= 36
    months = {
        *(r.vesting_month for r in stock),
        *(r.vesting_month for r in estate),
        *(r.vesting_month for r in insurance),
    }
    years = {m[:4] for m in months}
    assert len(years) >= 3
    # All three categories should be populated.
    assert stock and estate and insurance


# ---------------------------------------------------------------------------
# Sub-task 13 — stocks
# ---------------------------------------------------------------------------

def test_stocks_seeded(seeded_engine):
    engine, _ = seeded_engine
    with Session(engine) as s:
        parents = s.exec(select(StockJournal)).all()
        details = s.exec(select(StockDetail)).all()
    codes = {p.stock_code for p in parents}
    assert {"2330.TW", "AAPL"} <= codes
    assert 5 <= len(details) <= 20
    types = {d.excute_type for d in details}
    # Cover at least 3 of the 4 supported excute_type literals.
    assert len(types & {"buy", "sell", "stock", "cash"}) >= 3


# ---------------------------------------------------------------------------
# Sub-task 14 — estates cover all status values seeded
# ---------------------------------------------------------------------------

def test_estates_cover_all_status(seeded_engine):
    engine, _ = seeded_engine
    with Session(engine) as s:
        estates = s.exec(select(Estate)).all()
        journals = s.exec(select(EstateJournal)).all()
    statuses = {e.estate_status for e in estates}
    # Spec asks for own/rent/sold; live is the closest analogue to own — see
    # docstring of seed_estates() in seed_dev_data.py.
    assert {"live", "rent", "sold"} <= statuses
    counts: dict[str, int] = {}
    for j in journals:
        counts[j.estate_id] = counts.get(j.estate_id, 0) + 1
    for e in estates:
        assert counts.get(e.estate_id, 0) >= 1


# ---------------------------------------------------------------------------
# Sub-task 15 — insurances
# ---------------------------------------------------------------------------

def test_insurances_cover_has_closed(seeded_engine):
    engine, _ = seeded_engine
    with Session(engine) as s:
        rows = s.exec(select(Insurance)).all()
    flags = {r.has_closed for r in rows}
    assert flags == {"Y", "N"}


# ---------------------------------------------------------------------------
# Sub-task 16 — loans
# ---------------------------------------------------------------------------

def test_loan_repayed_matches_journal_sum(seeded_engine):
    engine, _ = seeded_engine
    with Session(engine) as s:
        loans = s.exec(select(Loan)).all()
        # Verify at least one loan has grace_expire_date populated.
        assert any(ln.grace_expire_date for ln in loans)
        for ln in loans:
            principal_sum = _scalar(
                s.exec(
                    select(func.coalesce(func.sum(LoanJournal.excute_price), 0.0))
                    .where(LoanJournal.loan_id == ln.loan_id)
                    .where(LoanJournal.loan_excute_type == "principal")
                ).one()
            )
            assert ln.repayed == principal_sum
            journals = s.exec(
                select(LoanJournal).where(LoanJournal.loan_id == ln.loan_id)
            ).all()
            assert len(journals) >= 5
            kinds = {j.loan_excute_type for j in journals}
            assert {"principal", "interest"} <= kinds


# ---------------------------------------------------------------------------
# Sub-task 17 — other-assets auto-index
# ---------------------------------------------------------------------------

def test_other_assets_auto_index(seeded_engine):
    engine, _ = seeded_engine
    with Session(engine) as s:
        rows = s.exec(select(OtherAsset)).all()
    assert len(rows) >= 6
    types = {r.asset_type for r in rows}
    assert len(types) >= 4
    # Auto-fill rows came after the explicit ones (max+1, max+2).
    explicit = sorted(
        [r for r in rows if r.asset_id.startswith("OA-") and r.asset_id not in ("OA-OTH-01", "OA-CASH-01")],
        key=lambda r: r.asset_index,
    )
    auto = sorted(
        [r for r in rows if r.asset_id in ("OA-OTH-01", "OA-CASH-01")],
        key=lambda r: r.asset_index,
    )
    assert all(r.asset_index >= 1 for r in rows)
    assert auto[0].asset_index == max(e.asset_index for e in explicit) + 1
    assert auto[1].asset_index == auto[0].asset_index + 1


# ---------------------------------------------------------------------------
# Sub-task 18 — dashboard fixtures
# ---------------------------------------------------------------------------

def test_dashboard_seeded(seeded_engine):
    engine, _ = seeded_engine
    with Session(engine) as s:
        targets = s.exec(select(TargetSetting)).all()
        fx = s.exec(select(FXRate)).all()
    years = {t.target_year for t in targets}
    assert len(years) == 3
    codes = {r.code for r in fx}
    assert {"TWD", "USD", "JPY"} <= codes


# ---------------------------------------------------------------------------
# Sub-task 19 — orchestrator returns counts
# ---------------------------------------------------------------------------

def test_run_seed_returns_counts(seeded_engine):
    _, counts = seeded_engine
    assert isinstance(counts, dict)
    assert counts
    for key, value in counts.items():
        assert isinstance(key, str)
        assert isinstance(value, int)
        assert value > 0
    # Spot-check key tables are present.
    assert "Account" in counts
    assert "Code_Data" in counts
    assert "Loan" in counts
    assert "Other_Asset" in counts
    assert "FX_Rate" in counts


# ---------------------------------------------------------------------------
# Sub-task 21 — module docstring
# ---------------------------------------------------------------------------

def test_module_docstring_documents_usage():
    doc = seed_dev_data.__doc__
    assert doc is not None
    assert len(doc) > 100
