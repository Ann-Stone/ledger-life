"""BE-005 — Migrator tests against the hand-crafted ``legacy_tiny.db`` fixture.

These tests never touch real legacy data. They use only
``tests/fixtures/legacy_tiny.db`` (rebuilt via
``tests/fixtures/build_legacy_tiny.py``).

Granular acceptance commands map to tests in this file as follows:

* sub-task 4   → ``test_migration_is_idempotent``
* sub-task 5   → ``test_account_migration_drops_carrier_no``
* sub-task 6   → ``test_credit_card_migration_drops_carrier_no``
* sub-task 7   → ``test_settings_tables_row_counts``
* sub-task 8   → ``test_journal_dates_iso`` (assertion: YYYYMMDD / YYYYMM,
                 per plan deviation — see plan file)
* sub-task 9   → ``test_asset_tables_row_counts``
* sub-task 10  → ``test_dashboard_tables_row_counts``
* sub-task 11  → ``test_initial_setting_skipped``
* sub-task 12  → ``test_camel_to_snake_normalization``
* sub-task 13  → ``test_end_to_end_row_counts_match``
* sub-task 14  → ``test_golden_fixture_migration``
* (expansion)  → ``test_snapshot_tables_row_counts``
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pytest
from sqlalchemy import inspect
from sqlmodel import Session, func, select

from scripts import migrate_from_legacy
from tests.fixtures import build_legacy_tiny
from scripts.migrate_from_legacy import (
    MigrationCountMismatch,
    _snake,
    _to_yyyymm,
    _to_yyyymmdd,
    run_migration,
)
from app.models.assets.estate import Estate, EstateJournal
from app.models.assets.estate_value_history import EstateValueHistory
from app.models.assets.insurance import Insurance, InsuranceJournal
from app.models.assets.insurance_value_history import InsuranceValueHistory
from app.models.assets.loan import Loan, LoanJournal
from app.models.assets.other_asset import OtherAsset
from app.models.assets.stock import StockDetail, StockJournal
from app.models.assets.stock_category import StockCategory
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
from app.models.monthly_report.loan_balance import LoanBalance
from app.models.monthly_report.stock_net_value_history import StockNetValueHistory
from app.models.settings.account import Account
from app.models.settings.alarm import Alarm
from app.models.settings.budget import Budget
from app.models.settings.code_data import CodeData
from app.models.settings.credit_card import CreditCard


FIXTURE = Path(__file__).resolve().parent / "fixtures" / "legacy_tiny.db"


def _scalar(n) -> int:
    if isinstance(n, tuple):
        return int(n[0])
    return int(n)


def _count(session: Session, model) -> int:
    return _scalar(session.exec(select(func.count()).select_from(model)).one())


@pytest.fixture
def target_engine(tmp_path: Path):
    """Per-test SQLite file engine; isolated from any real DB."""
    db_path = tmp_path / "target_test.db"
    engine = migrate_from_legacy._build_engine(f"sqlite:///{db_path}")
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture(scope="session")
def _legacy_fixture_path() -> Path:
    """Return the committed ``legacy_tiny.db`` fixture path.
    Only try to rebuild it if the file does not exist (allowing CI to run on the pre-committed db).
    """
    if not FIXTURE.exists():
        build_legacy_tiny.build(FIXTURE)
    return FIXTURE


@pytest.fixture
def legacy_conn(_legacy_fixture_path: Path):
    uri = f"file:{_legacy_fixture_path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# sub-task 4: idempotency
# ---------------------------------------------------------------------------

def test_migration_is_idempotent(legacy_conn, target_engine) -> None:
    first = run_migration(legacy_conn, target_engine, wipe=True)
    second = run_migration(legacy_conn, target_engine, wipe=True)
    assert first == second


# ---------------------------------------------------------------------------
# sub-task 5: Account drops carrier_no
# ---------------------------------------------------------------------------

def test_account_migration_drops_carrier_no(legacy_conn, target_engine) -> None:
    run_migration(legacy_conn, target_engine, wipe=True)
    insp = inspect(target_engine)
    cols = {c["name"] for c in insp.get_columns("Account")}
    assert "carrier_no" not in cols
    with Session(target_engine) as session:
        assert _count(session, Account) == 2


# ---------------------------------------------------------------------------
# sub-task 6: Credit_Card drops carrier_no
# ---------------------------------------------------------------------------

def test_credit_card_migration_drops_carrier_no(legacy_conn, target_engine) -> None:
    run_migration(legacy_conn, target_engine, wipe=True)
    insp = inspect(target_engine)
    cols = {c["name"] for c in insp.get_columns("Credit_Card")}
    assert "carrier_no" not in cols
    with Session(target_engine) as session:
        assert _count(session, CreditCard) == 2


# ---------------------------------------------------------------------------
# sub-task 7: settings tables row counts
# ---------------------------------------------------------------------------

def test_settings_tables_row_counts(legacy_conn, target_engine) -> None:
    run_migration(legacy_conn, target_engine, wipe=True)
    with Session(target_engine) as session:
        assert _count(session, CodeData) == 2
        assert _count(session, Account) == 2
        assert _count(session, CreditCard) == 2
        assert _count(session, Budget) == 2
        assert _count(session, Alarm) == 2


# ---------------------------------------------------------------------------
# sub-task 8: Journal dates normalized to YYYYMMDD / YYYYMM
# (Plan deviates from granular's "ISO 8601" wording — see plan file.)
# ---------------------------------------------------------------------------

def test_journal_dates_iso(legacy_conn, target_engine) -> None:
    run_migration(legacy_conn, target_engine, wipe=True)
    yyyymmdd = re.compile(r"^\d{8}$")
    yyyymm = re.compile(r"^\d{6}$")
    with Session(target_engine) as session:
        for j in session.exec(select(Journal)).all():
            assert yyyymmdd.fullmatch(j.spend_date), j.spend_date
            assert yyyymm.fullmatch(j.vesting_month), j.vesting_month


# ---------------------------------------------------------------------------
# sub-task 9: asset-domain row counts
# ---------------------------------------------------------------------------

def test_asset_tables_row_counts(legacy_conn, target_engine) -> None:
    run_migration(legacy_conn, target_engine, wipe=True)
    with Session(target_engine) as session:
        assert _count(session, OtherAsset) == 2
        assert _count(session, StockJournal) == 2
        assert _count(session, StockDetail) == 2
        assert _count(session, Insurance) == 2
        assert _count(session, InsuranceJournal) == 2
        assert _count(session, Estate) == 2
        assert _count(session, EstateJournal) == 2
        assert _count(session, Loan) == 2
        assert _count(session, LoanJournal) == 2


# ---------------------------------------------------------------------------
# sub-task 10: dashboard-domain row counts
# ---------------------------------------------------------------------------

def test_dashboard_tables_row_counts(legacy_conn, target_engine) -> None:
    run_migration(legacy_conn, target_engine, wipe=True)
    with Session(target_engine) as session:
        assert _count(session, FXRate) == 2
        assert _count(session, StockPriceHistory) == 2
        assert _count(session, TargetSetting) == 2


# ---------------------------------------------------------------------------
# Plan scope expansion: snapshot tables row counts
# ---------------------------------------------------------------------------

def test_snapshot_tables_row_counts(legacy_conn, target_engine) -> None:
    run_migration(legacy_conn, target_engine, wipe=True)
    with Session(target_engine) as session:
        assert _count(session, LoanBalance) == 2
        assert _count(session, StockNetValueHistory) == 2
        assert _count(session, InsuranceNetValueHistory) == 2
        assert _count(session, EstateNetValueHistory) == 2
        # Also verify monthly-report balance tables migrated.
        assert _count(session, AccountBalance) == 2
        assert _count(session, CreditCardBalance) == 2


# ---------------------------------------------------------------------------
# sub-task 11: Initial_Setting is skipped
# ---------------------------------------------------------------------------

def test_initial_setting_skipped(legacy_conn, target_engine) -> None:
    # Fixture has Initial_Setting with 1 row.
    src_count = legacy_conn.execute(
        "SELECT COUNT(*) AS n FROM Initial_Setting"
    ).fetchone()["n"]
    assert src_count == 1, "Fixture should contain 1 Initial_Setting row"

    run_migration(legacy_conn, target_engine, wipe=True)

    insp = inspect(target_engine)
    target_tables = set(insp.get_table_names())
    assert "Initial_Setting" not in target_tables


# ---------------------------------------------------------------------------
# sub-task 12: camelCase → snake_case helper
# ---------------------------------------------------------------------------

def test_camel_to_snake_normalization() -> None:
    assert _snake("creditCardIndex") == "credit_card_index"
    assert _snake("alreadySnakeCase") == "already_snake_case"
    assert _snake("XMLHttpRequest") == "x_m_l_http_request"  # naive helper is fine
    # Already snake-case input is preserved.
    assert _snake("account_id") == "account_id"
    assert _snake("expected_spend") == "expected_spend"


# ---------------------------------------------------------------------------
# sub-task 13: orchestrator row-count assertion
# ---------------------------------------------------------------------------

def test_end_to_end_row_counts_match(legacy_conn, target_engine) -> None:
    counts = run_migration(legacy_conn, target_engine, wipe=True)
    # Every retained table inserted exactly 2 rows into its primary target
    # (Estate_Journal/Insurance_Journal divert their extra appraisal rows).
    for table_name in (
        "Code_Data", "Account", "Credit_Card", "Budget", "Alarm",
        "Other_Asset", "Loan", "Loan_Journal", "Loan_Balance",
        "Stock_Journal", "Stock_Detail", "Stock_Net_Value_History",
        "Insurance", "Insurance_Journal", "Insurance_Net_Value_History",
        "Estate", "Estate_Journal", "Estate_Net_Value_History",
        "Journal", "Account_Balance", "Credit_Card_Balance",
        "FX_Rate", "Stock_Price_History", "Target_Setting",
    ):
        assert counts.get(table_name) == 2, f"{table_name} count mismatch: {counts.get(table_name)}"
    # Diversion side-targets and the re-seeded Stock_Category also report.
    assert counts.get("Estate_Value_History") == 1
    assert counts.get("Insurance_Value_History") == 1
    assert counts.get("Stock_Category") == 3


def test_orchestrator_raises_on_count_mismatch(legacy_conn, target_engine, monkeypatch) -> None:
    """Sanity check: if a migrator under-inserts, MigrationCountMismatch fires."""
    def bad_migrator(src, session):
        # Insert nothing — but fixture has 2 rows for Code_Data.
        return 0
    monkeypatch.setattr(migrate_from_legacy, "migrate_codes", bad_migrator)
    with pytest.raises(MigrationCountMismatch):
        run_migration(legacy_conn, target_engine, wipe=True)


# ---------------------------------------------------------------------------
# sub-task 14: golden fixture
# ---------------------------------------------------------------------------

def test_golden_fixture_migration(legacy_conn, target_engine) -> None:
    """Holistic check: full migration against the hand-crafted fixture."""
    counts = run_migration(legacy_conn, target_engine, wipe=True)

    # Every retained table → exactly 2 primary-target rows, plus the
    # diversion side-targets and the re-seeded Stock_Category.
    expected = {name: 2 for name in (
        "Code_Data", "Account", "Credit_Card", "Budget", "Alarm",
        "Other_Asset", "Loan", "Loan_Journal", "Loan_Balance",
        "Stock_Journal", "Stock_Detail", "Stock_Net_Value_History",
        "Insurance", "Insurance_Journal", "Insurance_Net_Value_History",
        "Estate", "Estate_Journal", "Estate_Net_Value_History",
        "Journal", "Account_Balance", "Credit_Card_Balance",
        "FX_Rate", "Stock_Price_History", "Target_Setting",
    )}
    expected["Estate_Value_History"] = 1
    expected["Insurance_Value_History"] = 1
    expected["Stock_Category"] = 3
    assert counts == expected

    # carrier_no must not appear in the target schema.
    insp = inspect(target_engine)
    assert "carrier_no" not in {c["name"] for c in insp.get_columns("Account")}
    assert "carrier_no" not in {c["name"] for c in insp.get_columns("Credit_Card")}

    # Initial_Setting must not have been created.
    assert "Initial_Setting" not in set(insp.get_table_names())

    # Account's legacy `carrier_no="DROP-ME-1"` must not leak into any text column.
    with Session(target_engine) as session:
        accounts = session.exec(select(Account)).all()
        for a in accounts:
            for value in (a.name, a.memo or "", a.owner or ""):
                assert "DROP-ME" not in value, f"Leaked carrier_no into {a!r}"
        cards = session.exec(select(CreditCard)).all()
        for c in cards:
            for value in (c.card_name, c.note or ""):
                assert "DROP" not in value, f"Leaked carrier_no into {c!r}"

        # FK reference translation: Loan.account_id should be the business
        # account_id string (FAKE-ACCT-01), not the legacy int "1".
        loans = session.exec(select(Loan).where(Loan.loan_id == "1")).all()
        assert loans, "Loan id=1 missing"
        assert loans[0].account_id == "FAKE-ACCT-01"

        # Insurance translates in_account_id/out_account_id INT → account_id str.
        ins = session.exec(select(Insurance).where(Insurance.insurance_id == "1")).all()
        assert ins, "Insurance id=1 missing"
        assert ins[0].in_account == "FAKE-ACCT-01"
        assert ins[0].out_account == "FAKE-ACCT-01"

        # Date normalization: Loan.apply_date "2020-01-01" → "20200101".
        loan_one = loans[0]
        assert loan_one.apply_date == "20200101"
        assert loan_one.grace_expire_date == "20200401"

        # Loan.repayed semantics: legacy 'N' flag → new 0.0 float.
        assert loan_one.repayed == 0.0


# ---------------------------------------------------------------------------
# Format normalizations for current-schema conventions
# ---------------------------------------------------------------------------

def test_alarm_dates_normalized(legacy_conn, target_engine) -> None:
    """Legacy 'MM/DD' anchors → BE-028 'MMDD'/'DD'; due_date → YYYYMM."""
    run_migration(legacy_conn, target_engine, wipe=True)
    with Session(target_engine) as session:
        yearly = session.exec(select(Alarm).where(Alarm.alarm_id == 1)).one()
        assert yearly.alarm_type == "Y"
        assert yearly.alarm_date == "0531"
        assert yearly.due_date == "202207"
        monthly = session.exec(select(Alarm).where(Alarm.alarm_id == 2)).one()
        assert monthly.alarm_type == "M"
        assert monthly.alarm_date == "15"
        assert monthly.due_date is None


def test_loan_interest_rate_percent_to_decimal(legacy_conn, target_engine) -> None:
    """Legacy percent form (1.31 = 1.31%) → new decimal form (0.0131)."""
    run_migration(legacy_conn, target_engine, wipe=True)
    with Session(target_engine) as session:
        rates = {
            loan.loan_id: loan.interest_rate
            for loan in session.exec(select(Loan)).all()
        }
    assert rates["1"] == pytest.approx(0.0131)
    assert rates["2"] == pytest.approx(0.025)


def test_credit_card_expiry_normalized(legacy_conn, target_engine) -> None:
    """All card_expiry values land as 'YYYY/MM', even datetime-string input."""
    run_migration(legacy_conn, target_engine, wipe=True)
    with Session(target_engine) as session:
        cards = {c.credit_card_id: c for c in session.exec(select(CreditCard)).all()}
    for card in cards.values():
        assert re.fullmatch(r"\d{4}/\d{2}", card.card_expiry), card.card_expiry
        assert card.limit_date is None
    assert cards["1"].card_expiry == "2026/08"
    assert cards["2"].card_expiry == "2022/07"


def test_insurance_pay_type_normalized(legacy_conn, target_engine) -> None:
    """Legacy cadence words remap: year → annual, month → monthly."""
    run_migration(legacy_conn, target_engine, wipe=True)
    with Session(target_engine) as session:
        policies = {i.insurance_id: i for i in session.exec(select(Insurance)).all()}
    assert policies["1"].pay_type == "annual"
    assert policies["1"].pay_day == "01/15"
    assert policies["2"].pay_type == "monthly"
    assert policies["2"].pay_day == "20"


def test_journal_spend_way_type_normalized(legacy_conn, target_engine) -> None:
    """'Credit_Card' lowers to 'credit_card'; other values pass through."""
    run_migration(legacy_conn, target_engine, wipe=True)
    with Session(target_engine) as session:
        journals = {j.distinct_number: j for j in session.exec(select(Journal)).all()}
    assert journals[1].spend_way_type == "account"
    assert journals[2].spend_way_type == "credit_card"
    assert all(j.spend_way_type != "Credit_Card" for j in journals.values())


# ---------------------------------------------------------------------------
# Appraisal-row diversion into the value-history tables
# ---------------------------------------------------------------------------

def test_estate_market_value_rows_diverted(legacy_conn, target_engine) -> None:
    """'marketValue' journals become Estate_Value_History (latest per month)."""
    run_migration(legacy_conn, target_engine, wipe=True)
    with Session(target_engine) as session:
        types = [j.estate_excute_type for j in session.exec(select(EstateJournal)).all()]
        assert "marketValue" not in types
        assert sorted(types) == ["fix", "tax"]
        history = session.exec(select(EstateValueHistory)).all()
        assert len(history) == 1
        entry = history[0]
        assert entry.estate_id == "1"
        assert entry.vesting_month == "202503"
        # Two same-month appraisals in the fixture — the later one wins.
        assert entry.market_value == 500000.0
        assert entry.memo == "newer appraisal"


def test_insurance_expect_rows_diverted(legacy_conn, target_engine) -> None:
    """'expect' journals become Insurance_Value_History entries."""
    run_migration(legacy_conn, target_engine, wipe=True)
    with Session(target_engine) as session:
        types = [
            j.insurance_excute_type
            for j in session.exec(select(InsuranceJournal)).all()
        ]
        assert "expect" not in types
        assert types == ["pay", "pay"]
        history = session.exec(select(InsuranceValueHistory)).all()
        assert len(history) == 1
        entry = history[0]
        assert entry.insurance_id == "1"
        assert entry.vesting_month == "202602"
        assert entry.surrender_value == 26000.0


# ---------------------------------------------------------------------------
# Stock_Category re-seeding after wipe
# ---------------------------------------------------------------------------

def test_stock_categories_seeded(legacy_conn, target_engine) -> None:
    counts = run_migration(legacy_conn, target_engine, wipe=True)
    assert counts["Stock_Category"] == 3
    with Session(target_engine) as session:
        rows = sorted(
            session.exec(select(StockCategory)).all(),
            key=lambda c: c.category_index,
        )
    assert [(c.category_id, c.name, c.in_use) for c in rows] == [
        ("SC-001", "成長型", "Y"),
        ("SC-002", "債券", "Y"),
        ("SC-003", "類現金", "Y"),
    ]
    # Re-running with wipe re-seeds to exactly 3 again (idempotent).
    counts2 = run_migration(legacy_conn, target_engine, wipe=True)
    assert counts2["Stock_Category"] == 3
    with Session(target_engine) as session:
        assert _count(session, StockCategory) == 3


# ---------------------------------------------------------------------------
# Date helper unit tests (support sub-task 8)
# ---------------------------------------------------------------------------

def test_to_yyyymmdd_handles_iso_and_passthrough() -> None:
    assert _to_yyyymmdd("2026-04-18") == "20260418"
    assert _to_yyyymmdd("20260418") == "20260418"
    assert _to_yyyymmdd("2026-04-18 00:00:00") == "20260418"
    assert _to_yyyymmdd(None) is None
    assert _to_yyyymmdd("") is None


def test_to_yyyymm_handles_iso_and_passthrough() -> None:
    assert _to_yyyymm("202604") == "202604"
    assert _to_yyyymm("2026-04-18") == "202604"
    assert _to_yyyymm(None) is None
