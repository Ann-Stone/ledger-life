"""Dev-only seed data script for the live networth-api SQLite database.

Invocation:
    uv run python scripts/seed_dev_data.py [--target-db-url sqlite:///path.db] [--no-wipe]

Default target is ``app.config.settings.database_url`` (typically
``sqlite:///~/.networth/networth.db``). The script wipes (drop_all +
create_all) the target schema and re-loads a curated, idempotent fixture
covering every domain — Settings, Monthly Report, Assets, Dashboard.

Dev-only restriction
    The target URL is validated by ``_assert_dev_db``: it must be a
    ``sqlite:///`` URL whose file lives under ``~/.networth/`` or whose
    filename ends with ``_dev.db``, ``_test.db``, or ``seed_test.db``.
    Anything containing ``prod`` or any non-SQLite scheme is rejected.
    ``sqlite:///:memory:`` is allowed for tests.

Idempotency
    Re-running the script (with default ``--wipe``) produces identical
    state — same row counts per table, same FK consistency. The wipe is
    the only supported reset strategy; this ticket does not ship a
    selective unseed.

Server-semantic fidelity
    ``Loan.repayed`` is recomputed via ``asset_service._recalculate_repayed``
    after the ``Loan_Journal`` rows are inserted. Two ``Other_Asset`` rows
    are inserted with ``asset_index=None`` via
    ``asset_service.create_other_asset`` so the auto-fill (``max+1``) path
    is exercised.

This is **not** the BE-005 legacy data migration. BE-005 imports the old
``account-book-API`` SQLite into the new schema; this script ships
hand-written fixtures for backend dev convenience only.
"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Iterable

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, func, select

import app.models  # noqa: F401  registers tables on SQLModel.metadata
from app.config import settings as app_settings
from app.database import SQLITE_PREFIX, _resolve_sqlite_url
from app.models.assets.estate import Estate, EstateJournal
from app.models.assets.insurance import Insurance, InsuranceJournal
from app.models.assets.loan import Loan, LoanJournal
from app.models.assets.other_asset import OtherAsset, OtherAssetCreate
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
from app.models.monthly_report.loan_balance import LoanBalance
from app.models.monthly_report.stock_net_value_history import StockNetValueHistory
from app.models.settings.account import Account
from app.models.settings.alarm import Alarm
from app.models.settings.budget import Budget
from app.models.settings.code_data import CodeData
from app.models.settings.credit_card import CreditCard
from app.services.asset_service import _recalculate_repayed, create_other_asset


DEV_HOME_DIR = Path("~/.networth/").expanduser().resolve()
DEV_SUFFIXES = ("_dev.db", "_test.db", "seed_test.db")
TODAY = datetime(2026, 5, 9)


# ---------------------------------------------------------------------------
# Dev guard, engine builder, schema reset
# ---------------------------------------------------------------------------

def _assert_dev_db(url: str) -> None:
    """Reject URLs that don't look like a developer's local SQLite file."""
    lowered = url.lower()
    if not url.startswith(SQLITE_PREFIX):
        raise RuntimeError(
            f"Refusing to seed non-SQLite target: {url!r}. "
            "Dev seed runs only against sqlite:/// URLs."
        )
    if "prod" in lowered:
        raise RuntimeError(
            f"Refusing to seed production-pattern URL: {url!r} "
            "(contains 'prod')."
        )
    raw = url[len(SQLITE_PREFIX):]
    if raw == ":memory:":
        return
    resolved_url = _resolve_sqlite_url(url)
    path = Path(resolved_url[len(SQLITE_PREFIX):]).resolve()
    if any(path.name.endswith(suf) for suf in DEV_SUFFIXES):
        return
    try:
        path.relative_to(DEV_HOME_DIR)
        return
    except ValueError:
        pass
    raise RuntimeError(
        f"Refusing to seed: {url!r} is not a recognised dev DB path. "
        f"Use a path under {DEV_HOME_DIR} or a filename ending in "
        f"{DEV_SUFFIXES}."
    )


def _build_engine(url: str):
    """Create a fresh SQLModel engine for the given URL."""
    resolved = _resolve_sqlite_url(url)
    raw = resolved[len(SQLITE_PREFIX):]
    if raw == ":memory:":
        return create_engine(
            resolved,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    return create_engine(resolved, connect_args={"check_same_thread": False})


def _reset_target(engine) -> None:
    """Drop and re-create every table registered on SQLModel.metadata."""
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def _ym_offset(year: int, month: int, delta_months: int) -> tuple[int, int]:
    total = year * 12 + (month - 1) + delta_months
    return total // 12, (total % 12) + 1


def _ymd(year: int, month: int, day: int) -> str:
    return f"{year:04d}{month:02d}{day:02d}"


def _ym(year: int, month: int) -> str:
    return f"{year:04d}{month:02d}"


# ---------------------------------------------------------------------------
# Seed fixtures
# ---------------------------------------------------------------------------

def seed_accounts(session: Session) -> list[Account]:
    rows = [
        Account(
            account_id="BANK-CASH-01",
            name="Wallet Cash",
            account_type="cash",
            fx_code="TWD",
            is_calculate="Y",
            in_use="Y",
            discount=1.0,
            memo="Pocket money",
            owner=None,
            account_index=1,
        ),
        Account(
            account_id="BANK-CHASE-01",
            name="Chase Checking",
            account_type="bank",
            fx_code="USD",
            is_calculate="Y",
            in_use="Y",
            discount=1.0,
            memo="Primary USD checking",
            owner="stone",
            account_index=2,
        ),
        Account(
            account_id="INVEST-IB-01",
            name="Interactive Brokers",
            account_type="broker",
            fx_code="USD",
            is_calculate="Y",
            in_use="Y",
            discount=1.0,
            memo="Brokerage",
            owner="stone",
            account_index=3,
        ),
        Account(
            account_id="BANK-CTBC-01",
            name="CTBC Savings",
            account_type="bank",
            fx_code="TWD",
            is_calculate="Y",
            in_use="N",
            discount=1.0,
            memo="Retired savings",
            owner=None,
            account_index=4,
        ),
    ]
    for r in rows:
        session.add(r)
    session.commit()
    for r in rows:
        session.refresh(r)
    return rows


def seed_codes(session: Session) -> tuple[list[CodeData], list[CodeData]]:
    """Five main codes (one per code_type), each with two sub-codes."""
    main_specs = [
        ("FLT-MAIN", "Floating", "飲食"),
        ("FIX-MAIN", "Fixed", "房租"),
        ("INV-MAIN", "Invest", "股票投資"),
        ("INC-MAIN", "Income", "薪資"),
        ("TRF-MAIN", "Transfer", "轉帳"),
    ]
    sub_specs = [
        ("FLT-SUB-01", "FLT-MAIN", "Floating", "早餐"),
        ("FLT-SUB-02", "FLT-MAIN", "Floating", "午餐"),
        ("FIX-SUB-01", "FIX-MAIN", "Fixed", "房租"),
        ("FIX-SUB-02", "FIX-MAIN", "Fixed", "水電"),
        ("INV-SUB-01", "INV-MAIN", "Invest", "台股"),
        ("INV-SUB-02", "INV-MAIN", "Invest", "美股"),
        ("INC-SUB-01", "INC-MAIN", "Income", "本薪"),
        ("INC-SUB-02", "INC-MAIN", "Income", "獎金"),
        ("TRF-SUB-01", "TRF-MAIN", "Transfer", "帳戶轉帳"),
        ("TRF-SUB-02", "TRF-MAIN", "Transfer", "信用卡繳款"),
    ]
    mains: list[CodeData] = []
    for idx, (code_id, code_type, name) in enumerate(main_specs, start=1):
        row = CodeData(
            code_id=code_id,
            code_type=code_type,
            name=name,
            parent_id=None,
            in_use="Y",
            code_index=idx,
        )
        session.add(row)
        mains.append(row)
    session.commit()
    subs: list[CodeData] = []
    for idx, (code_id, parent_id, code_type, name) in enumerate(sub_specs, start=1):
        row = CodeData(
            code_id=code_id,
            code_type=code_type,
            name=name,
            parent_id=parent_id,
            in_use="Y",
            code_index=idx,
        )
        session.add(row)
        subs.append(row)
    session.commit()
    for r in mains + subs:
        session.refresh(r)
    return mains, subs


def seed_credit_cards(session: Session) -> list[CreditCard]:
    rows = [
        CreditCard(
            credit_card_id="CC-VISA-01",
            card_name="Chase Sapphire Visa",
            card_no="4111-XXXX-XXXX-1111",
            last_day=25,
            charge_day=15,
            limit_date=20,
            feedback_way="cashback",
            fx_code="USD",
            in_use="Y",
            credit_card_index=1,
            note="Primary travel card",
        ),
        CreditCard(
            credit_card_id="CC-MASTER-01",
            card_name="CTBC MasterCard",
            card_no="5500-XXXX-XXXX-2222",
            last_day=20,
            charge_day=10,
            limit_date=15,
            feedback_way="points",
            fx_code="TWD",
            in_use="Y",
            credit_card_index=2,
            note="Daily TWD spend",
        ),
        CreditCard(
            credit_card_id="CC-AMEX-01",
            card_name="Amex Gold",
            card_no="3700-XXXXXX-X3333",
            last_day=28,
            charge_day=18,
            limit_date=23,
            feedback_way="miles",
            fx_code="USD",
            in_use="N",
            credit_card_index=3,
            note="Retired card",
        ),
    ]
    for r in rows:
        session.add(r)
    session.commit()
    for r in rows:
        session.refresh(r)
    return rows


def seed_budgets(session: Session, *, codes_main: list[CodeData]) -> list[Budget]:
    years = [str(TODAY.year - 1), str(TODAY.year)]
    rows: list[Budget] = []
    for year in years:
        for idx, code in enumerate(codes_main, start=1):
            base = 1000.0 * idx
            row = Budget(
                budget_year=year,
                category_code=code.code_id,
                category_name=code.name,
                code_type=code.code_type,
                **{f"expected{m:02d}": base + m * 10.0 for m in range(1, 13)},
            )
            session.add(row)
            rows.append(row)
    session.commit()
    return rows


def seed_alarms(session: Session) -> list[Alarm]:
    specs = [
        ("保單續期", "20260601", "Whole-life policy renewal", "20260615"),
        ("信用卡帳單", "20260520", "Visa statement due", "20260525"),
        ("房屋稅", "20260701", "Property tax", None),
        ("健檢", "20260910", "Annual health check", None),
        ("訂閱續訂", "20260615", "Streaming subscription renewal", None),
    ]
    rows = []
    for alarm_type, alarm_date, content, due_date in specs:
        row = Alarm(
            alarm_type=alarm_type,
            alarm_date=alarm_date,
            content=content,
            due_date=due_date,
        )
        session.add(row)
        rows.append(row)
    session.commit()
    for r in rows:
        session.refresh(r)
    return rows


def seed_journals(
    session: Session,
    *,
    accounts: list[Account],
    credit_cards: list[CreditCard],
    codes_main: list[CodeData],
    codes_sub: list[CodeData],
) -> list[Journal]:
    main_by_type = {c.code_type: c for c in codes_main}
    sub_by_parent: dict[str, list[CodeData]] = {}
    for s in codes_sub:
        sub_by_parent.setdefault(s.parent_id or "", []).append(s)
    main_types = ["Floating", "Fixed", "Income", "Invest", "Transfer"]
    rows: list[Journal] = []
    for i in range(30):
        delta = -(i % 24)
        year, month = _ym_offset(TODAY.year, TODAY.month, delta)
        day = (i % 27) + 1
        spend_date = _ymd(year, month, day)
        vesting_month = _ym(year, month)
        main_type = main_types[i % 5]
        main = main_by_type[main_type]
        if i % 2 == 0:
            way_row = accounts[i % len(accounts)]
            way_value = way_row.account_id
            way_type = "account"
            way_table = "Account"
        else:
            card = credit_cards[i % len(credit_cards)]
            way_value = card.credit_card_id
            way_type = "credit_card"
            way_table = "Credit_Card"
        if i % 6 == 0 and main.code_id in sub_by_parent:
            sub_row = sub_by_parent[main.code_id][0]
            action_sub = sub_row.code_id
            action_sub_type = sub_row.code_type
            action_sub_table = "Code_Data"
        else:
            action_sub = None
            action_sub_type = None
            action_sub_table = None
        spending = (100.0 + i) if main_type == "Income" else -(50.0 + i)
        invoice = f"AB1234567{i}" if i < 2 else None
        row = Journal(
            vesting_month=vesting_month,
            spend_date=spend_date,
            spend_way=way_value,
            spend_way_type=way_type,
            spend_way_table=way_table,
            action_main=main.code_id,
            action_main_type=main_type,
            action_main_table="Code_Data",
            action_sub=action_sub,
            action_sub_type=action_sub_type,
            action_sub_table=action_sub_table,
            spending=spending,
            invoice_number=invoice,
            note=f"Seed journal {i}",
        )
        session.add(row)
        rows.append(row)
    session.commit()
    for r in rows:
        session.refresh(r)
    return rows


def seed_settled_month(
    session: Session,
    *,
    accounts: list[Account],
    credit_cards: list[CreditCard],
) -> dict:
    """Settle the most-recent 13 fully-closed months.

    Dashboard verification (asset_debt_trend stacked-area chart) needs at least
    13 monthly snapshots across all six balance/net-value tables; one snapshot
    yields a flat line that cannot exercise the chart's per-category trend
    rendering. Offsets -14..-2 from TODAY produce 13 consecutive periods
    ending two months before today (the last fully-closed month under the
    rest of the seed's conventions).
    """
    fx_rate_for = {"TWD": 1.0, "USD": 31.5, "JPY": 0.21}
    vesting_months: list[str] = []
    last: dict = {}
    for offset in range(-14, -1):  # -14..-2 inclusive: 13 months
        year, month = _ym_offset(TODAY.year, TODAY.month, offset)
        vesting_month = _ym(year, month)
        vesting_months.append(vesting_month)
        delta_idx = offset + 14  # 0..12
        mult = 1.0 + delta_idx * 0.02

        ab_rows: list[AccountBalance] = []
        for idx, acc in enumerate(accounts, start=1):
            ab = AccountBalance(
                vesting_month=vesting_month,
                id=acc.account_id,
                name=acc.name,
                balance=10000.0 * idx * mult,
                fx_code=acc.fx_code,
                fx_rate=fx_rate_for.get(acc.fx_code, 1.0),
                is_calculate=acc.is_calculate,
            )
            session.add(ab)
            ab_rows.append(ab)

        cc_rows: list[CreditCardBalance] = []
        for idx, card in enumerate(credit_cards, start=1):
            cb = CreditCardBalance(
                vesting_month=vesting_month,
                id=card.credit_card_id,
                name=card.card_name,
                balance=-1000.0 * idx * mult,
                fx_rate=fx_rate_for.get(card.fx_code, 1.0),
            )
            session.add(cb)
            cc_rows.append(cb)

        nv = StockNetValueHistory(
            vesting_month=vesting_month,
            id="STK-H-SETTLED",
            asset_id="AC-STK-001",
            stock_code="AAPL",
            stock_name="Apple Inc.",
            amount=50.0,
            price=180.50 * mult,
            cost=8000.0,
            fx_code="USD",
            fx_rate=31.5,
        )
        session.add(nv)

        lb = LoanBalance(
            vesting_month=vesting_month,
            id="LN-MORT-01",
            name="Home Mortgage",
            balance=-240000.0 + delta_idx * 1500.0,
            cost=250000.0,
            fx_code="TWD",
            fx_rate=1.0,
        )
        session.add(lb)

        est = EstateNetValueHistory(
            vesting_month=vesting_month,
            id="EST-SETTLED",
            asset_id="AC-REAL-SETTLED",
            name="Settled condo",
            market_value=480000.0 * mult,
            cost=420000.0,
            estate_status="live",
            fx_code="TWD",
            fx_rate=1.0,
        )
        session.add(est)

        ins = InsuranceNetValueHistory(
            vesting_month=vesting_month,
            id="INS-SETTLED",
            asset_id="AC-INS-SETTLED",
            name="Settled policy",
            surrender_value=24000.0 * mult,
            cost=20000.0,
            fx_code="USD",
            fx_rate=31.5,
        )
        session.add(ins)

        if offset == -2:
            last = {
                "vesting_month": vesting_month,
                "account_balances": ab_rows,
                "credit_card_balances": cc_rows,
                "stock_net_value": nv,
                "loan_balance": lb,
            }

    session.commit()
    return {**last, "vesting_months": vesting_months}


def seed_stock_prices(session: Session) -> list[StockPriceHistory]:
    rows: list[StockPriceHistory] = []
    for code, base in (("2330.TW", 800.0), ("AAPL", 180.0)):
        for delta in range(0, 6):
            year, month = _ym_offset(TODAY.year, TODAY.month, -delta)
            fetch_date = _ymd(year, month, 15)
            price = base + delta
            rows.append(
                StockPriceHistory(
                    stock_code=code,
                    fetch_date=fetch_date,
                    open_price=price - 1.0,
                    highest_price=price + 2.0,
                    lowest_price=price - 2.0,
                    close_price=price,
                )
            )
    for r in rows:
        session.add(r)
    session.commit()
    return rows


def seed_year_report_history(session: Session) -> dict:
    """36 monthly snapshots over 3 years across 3 net-value categories."""
    stock_rows: list[StockNetValueHistory] = []
    estate_rows: list[EstateNetValueHistory] = []
    insurance_rows: list[InsuranceNetValueHistory] = []
    for delta in range(36):
        year, month = _ym_offset(TODAY.year, TODAY.month, -(delta + 3))
        vesting_month = _ym(year, month)
        bucket = delta % 3
        if bucket == 0:
            stock_rows.append(
                StockNetValueHistory(
                    vesting_month=vesting_month,
                    id="STK-H-YR",
                    asset_id="AC-STK-YR",
                    stock_code="AAPL",
                    stock_name="Apple Inc.",
                    amount=10.0 + delta,
                    price=180.0 + delta,
                    cost=1500.0 + delta * 10,
                    fx_code="USD",
                    fx_rate=31.5,
                )
            )
        elif bucket == 1:
            estate_rows.append(
                EstateNetValueHistory(
                    vesting_month=vesting_month,
                    id="EST-YR",
                    asset_id="AC-REAL-YR",
                    name="Year-report condo",
                    market_value=500000.0 + delta * 100,
                    cost=420000.0,
                    estate_status="live",
                    fx_code="TWD",
                    fx_rate=1.0,
                )
            )
        else:
            insurance_rows.append(
                InsuranceNetValueHistory(
                    vesting_month=vesting_month,
                    id="INS-YR",
                    asset_id="AC-INS-YR",
                    name="Year-report policy",
                    surrender_value=25000.0 + delta * 50,
                    cost=20000.0,
                    fx_code="USD",
                    fx_rate=31.5,
                )
            )
    for r in stock_rows + estate_rows + insurance_rows:
        session.add(r)
    session.commit()
    return {
        "stock": stock_rows,
        "estate": estate_rows,
        "insurance": insurance_rows,
    }


def seed_stocks(session: Session) -> tuple[list[StockJournal], list[StockDetail]]:
    parents = [
        StockJournal(
            stock_id="STK-H-001",
            stock_code="2330.TW",
            stock_name="TSMC",
            asset_id="AC-STK-TW",
            expected_spend=80000.0,
        ),
        StockJournal(
            stock_id="STK-H-002",
            stock_code="AAPL",
            stock_name="Apple Inc.",
            asset_id="AC-STK-US",
            expected_spend=10000.0,
        ),
    ]
    for p in parents:
        session.add(p)
    session.commit()
    detail_specs = [
        ("STK-H-001", "buy", 100.0, 800.0, "20240115", "BANK-CTBC-01", "CTBC Savings"),
        ("STK-H-001", "buy", 50.0, 820.0, "20240615", "BANK-CTBC-01", "CTBC Savings"),
        ("STK-H-001", "sell", 30.0, 850.0, "20251010", "BANK-CTBC-01", "CTBC Savings"),
        ("STK-H-001", "cash", 0.0, 1500.0, "20251220", "BANK-CTBC-01", "CTBC Savings"),
        ("STK-H-002", "buy", 20.0, 175.0, "20240220", "INVEST-IB-01", "Interactive Brokers"),
        ("STK-H-002", "buy", 10.0, 190.0, "20250315", "INVEST-IB-01", "Interactive Brokers"),
        ("STK-H-002", "stock", 1.0, 0.0, "20251101", "INVEST-IB-01", "Interactive Brokers"),
        ("STK-H-002", "sell", 5.0, 200.0, "20260105", "INVEST-IB-01", "Interactive Brokers"),
    ]
    details: list[StockDetail] = []
    for stock_id, kind, amt, price, date_, acc_id, acc_name in detail_specs:
        det = StockDetail(
            stock_id=stock_id,
            excute_type=kind,
            excute_amount=amt,
            excute_price=price,
            excute_date=date_,
            account_id=acc_id,
            account_name=acc_name,
            memo=f"{kind} {stock_id}",
        )
        session.add(det)
        details.append(det)
    session.commit()
    for r in parents + details:
        session.refresh(r)
    return parents, details


def seed_estates(session: Session) -> tuple[list[Estate], list[EstateJournal]]:
    """One per realised estate_status: live / rent / sold.

    Note: ticket spec lists 'own/rent/sold' but the actual SQLModel literal
    is ``Literal['idle','live','rent','sold']``. 'live' (= primary residence)
    is the closest analogue to 'own'.
    """
    estates = [
        Estate(
            estate_id="EST-LIVE-01",
            estate_name="Family Condo",
            estate_type="residential",
            estate_address="123 Main St",
            asset_id="AC-REAL-LIVE",
            obtain_date="20200101",
            loan_id=None,
            estate_status="live",
            memo="Primary residence",
        ),
        Estate(
            estate_id="EST-RENT-01",
            estate_name="Rental Studio",
            estate_type="residential",
            estate_address="456 Pine Ave",
            asset_id="AC-REAL-RENT",
            obtain_date="20210601",
            loan_id=None,
            estate_status="rent",
            memo="Tenant occupied",
        ),
        Estate(
            estate_id="EST-SOLD-01",
            estate_name="Old Apartment",
            estate_type="residential",
            estate_address="789 Old Rd",
            asset_id="AC-REAL-SOLD",
            obtain_date="20180101",
            loan_id=None,
            estate_status="sold",
            memo="Sold 2024",
        ),
    ]
    for e in estates:
        session.add(e)
    session.commit()
    journal_rows: list[EstateJournal] = []
    for est in estates:
        journal_rows.append(
            EstateJournal(
                estate_id=est.estate_id,
                estate_excute_type="tax",
                excute_price=5000.0,
                excute_date="20250101",
                memo=f"Property tax {est.estate_id}",
            )
        )
        journal_rows.append(
            EstateJournal(
                estate_id=est.estate_id,
                estate_excute_type="fix",
                excute_price=2500.0,
                excute_date="20250601",
                memo=f"Maintenance {est.estate_id}",
            )
        )
    for j in journal_rows:
        session.add(j)
    session.commit()
    for r in estates + journal_rows:
        session.refresh(r)
    return estates, journal_rows


def seed_insurances(session: Session) -> list[Insurance]:
    rows = [
        Insurance(
            insurance_id="INS-OPEN-01",
            insurance_name="Whole life policy",
            asset_id="AC-INS-WL",
            in_account="BANK-CHASE-01",
            out_account="BANK-CHASE-01",
            start_date="20200101",
            end_date="20500101",
            pay_type="annual",
            pay_day=15,
            expected_spend=1200.0,
            has_closed="N",
        ),
        Insurance(
            insurance_id="INS-CLOSED-01",
            insurance_name="Term life policy",
            asset_id="AC-INS-TERM",
            in_account="BANK-CHASE-01",
            out_account="BANK-CHASE-01",
            start_date="20100101",
            end_date="20240101",
            pay_type="annual",
            pay_day=20,
            expected_spend=800.0,
            has_closed="Y",
        ),
    ]
    for r in rows:
        session.add(r)
    session.commit()
    journals = [
        InsuranceJournal(
            insurance_id="INS-OPEN-01",
            insurance_excute_type="pay",
            excute_price=1200.0,
            excute_date="20250115",
            memo="Annual premium 2025",
        ),
        InsuranceJournal(
            insurance_id="INS-OPEN-01",
            insurance_excute_type="pay",
            excute_price=1200.0,
            excute_date="20260115",
            memo="Annual premium 2026",
        ),
    ]
    for j in journals:
        session.add(j)
    session.commit()
    for r in rows:
        session.refresh(r)
    return rows


def seed_loans(session: Session) -> tuple[list[Loan], list[LoanJournal]]:
    """Two loans (one with grace_expire_date) plus journals split principal/interest.

    Loan.repayed is recomputed via asset_service._recalculate_repayed after
    the journal rows are inserted, mirroring real-server behaviour.
    """
    loans = [
        Loan(
            loan_id="LN-MORT-01",
            loan_name="Home Mortgage",
            loan_type="mortgage",
            account_id="BANK-CHASE-01",
            account_name="Chase Checking",
            interest_rate=0.035,
            period=360,
            apply_date="20200101",
            grace_expire_date="20200401",
            pay_day=1,
            amount=250000.0,
            repayed=0.0,
            loan_index=1,
        ),
        Loan(
            loan_id="LN-AUTO-01",
            loan_name="Auto Loan",
            loan_type="auto",
            account_id="BANK-CTBC-01",
            account_name="CTBC Savings",
            interest_rate=0.045,
            period=60,
            apply_date="20230301",
            grace_expire_date=None,
            pay_day=10,
            amount=20000.0,
            repayed=0.0,
            loan_index=2,
        ),
    ]
    for ln in loans:
        session.add(ln)
    session.commit()
    journals: list[LoanJournal] = []
    for ln in loans:
        for i in range(6):
            kind = "principal" if i % 2 == 0 else "interest"
            price = 1500.0 if kind == "principal" else 600.0
            journals.append(
                LoanJournal(
                    loan_id=ln.loan_id,
                    loan_excute_type=kind,
                    excute_price=price,
                    excute_date=_ymd(2025, (i % 12) + 1, 15),
                    memo=f"{kind} {i} for {ln.loan_id}",
                )
            )
    for j in journals:
        session.add(j)
    session.commit()
    for ln in loans:
        _recalculate_repayed(session, ln.loan_id)
    for ln in loans:
        session.refresh(ln)
    return loans, journals


def seed_other_assets(session: Session) -> list[OtherAsset]:
    """6 rows across ≥4 asset_types; 2 inserted via service-layer auto-fill."""
    explicit_rows = [
        OtherAsset(
            asset_id="OA-STK-01",
            asset_name="US Equities Bucket",
            asset_type="stock",
            in_use="Y",
            asset_index=1,
        ),
        OtherAsset(
            asset_id="OA-INS-01",
            asset_name="Insurance Bucket",
            asset_type="insurance",
            in_use="Y",
            asset_index=2,
        ),
        OtherAsset(
            asset_id="OA-EST-01",
            asset_name="Real Estate Bucket",
            asset_type="estate",
            in_use="Y",
            asset_index=3,
        ),
        OtherAsset(
            asset_id="OA-LOAN-01",
            asset_name="Loan Bucket",
            asset_type="loan",
            in_use="Y",
            asset_index=4,
        ),
    ]
    for r in explicit_rows:
        session.add(r)
    session.commit()
    auto_specs = [
        ("OA-OTH-01", "Misc Other Asset", "other"),
        ("OA-CASH-01", "Cash-equivalents", "cash"),
    ]
    auto_rows: list[OtherAsset] = []
    for asset_id, name, asset_type in auto_specs:
        payload = OtherAssetCreate(
            asset_id=asset_id,
            asset_name=name,
            asset_type=asset_type,
            in_use="Y",
            asset_index=None,
        )
        auto_rows.append(create_other_asset(session, payload))
    return explicit_rows + auto_rows


def seed_targets_and_fx(session: Session) -> dict:
    targets = [
        TargetSetting(
            distinct_number=f"T-{year}-01",
            target_year=str(year),
            setting_value=1_000_000.0 * (year - TODAY.year + 1),
            is_done="N",
        )
        for year in (TODAY.year + 1, TODAY.year + 2, TODAY.year + 3)
    ]
    for t in targets:
        session.add(t)
    fx_date = _ymd(TODAY.year, TODAY.month, 1)
    fx_rows = [
        FXRate(import_date=fx_date, code="TWD", buy_rate=1.0),
        FXRate(import_date=fx_date, code="USD", buy_rate=31.52),
        FXRate(import_date=fx_date, code="JPY", buy_rate=0.21),
    ]
    for r in fx_rows:
        session.add(r)
    session.commit()
    for r in targets + fx_rows:
        session.refresh(r)
    return {"targets": targets, "fx": fx_rows}


# ---------------------------------------------------------------------------
# Orchestrator + CLI
# ---------------------------------------------------------------------------

TABLES_TO_COUNT = (
    Account,
    CodeData,
    CreditCard,
    Budget,
    Alarm,
    Journal,
    AccountBalance,
    CreditCardBalance,
    StockNetValueHistory,
    EstateNetValueHistory,
    InsuranceNetValueHistory,
    LoanBalance,
    StockPriceHistory,
    StockJournal,
    StockDetail,
    Estate,
    EstateJournal,
    Insurance,
    InsuranceJournal,
    Loan,
    LoanJournal,
    OtherAsset,
    FXRate,
    TargetSetting,
)


def _scalar(value) -> int:
    if isinstance(value, tuple):
        return int(value[0])
    return int(value)


def run_seed(engine) -> dict[str, int]:
    """Run every seed_* in FK-safe order and return per-table row counts."""
    with Session(engine) as session:
        accounts = seed_accounts(session)
        codes_main, codes_sub = seed_codes(session)
        credit_cards = seed_credit_cards(session)
        seed_budgets(session, codes_main=codes_main)
        seed_alarms(session)
        seed_journals(
            session,
            accounts=accounts,
            credit_cards=credit_cards,
            codes_main=codes_main,
            codes_sub=codes_sub,
        )
        seed_settled_month(session, accounts=accounts, credit_cards=credit_cards)
        seed_stock_prices(session)
        seed_stocks(session)
        seed_estates(session)
        seed_insurances(session)
        seed_loans(session)
        seed_other_assets(session)
        seed_year_report_history(session)
        seed_targets_and_fx(session)
        session.commit()

        counts: dict[str, int] = {}
        for model in TABLES_TO_COUNT:
            n = session.exec(select(func.count()).select_from(model)).one()
            counts[model.__tablename__] = _scalar(n)
    print(counts)
    return counts


def main(target_db_url: str | None = None, wipe: bool = True) -> dict[str, int]:
    url = target_db_url or app_settings.database_url
    _assert_dev_db(url)
    engine = _build_engine(url)
    if wipe:
        _reset_target(engine)
    try:
        return run_seed(engine)
    finally:
        engine.dispose()


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="seed_dev_data",
        description=(
            "Dev-only seed loader for the networth-api SQLite DB. "
            "Wipes and re-loads a curated fixture set. Refuses to run "
            "against production-pattern URLs."
        ),
    )
    parser.add_argument(
        "--target-db-url",
        default=None,
        help=(
            "Override the target database URL. Defaults to "
            "app.config.settings.database_url. Must be a sqlite:/// URL "
            "under ~/.networth/ or named *_dev.db / *_test.db."
        ),
    )
    parser.add_argument(
        "--no-wipe",
        dest="wipe",
        action="store_false",
        help="Skip drop_all + create_all before seeding (not idempotent).",
    )
    parser.set_defaults(wipe=True)
    return parser


def _cli_entry(argv: Iterable[str] | None = None) -> None:
    parser = _build_arg_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    main(target_db_url=args.target_db_url, wipe=args.wipe)


if __name__ == "__main__":
    _cli_entry()
