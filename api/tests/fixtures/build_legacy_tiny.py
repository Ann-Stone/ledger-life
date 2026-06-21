"""Build the hand-crafted ``legacy_tiny.db`` fixture used by BE-005 tests.

Why this exists
---------------
The BE-005 data migrator must be exercised without touching the real
``ledger.db``. This script writes a deterministic SQLite file containing
the legacy schema plus a handful of synthetic rows per retained table
mirroring real-world value shapes: 'MM/DD' alarm anchors, percent-form
loan rates, datetime-string card expiries, a NEGATIVE-magnitude loan
``principal`` row (to prove the sign-normalization abs()),
``marketValue``/``expect`` appraisal journal rows (to prove the
value-history diversion), a ``spend_way_type='Credit_Card'`` journal,
one ``Account``/``Credit_Card`` row with a ``carrier_no`` value (to prove
the drop), and a single ``Initial_Setting`` row (to prove the skip).

The legacy schema used to be read at build time from
``account-book-API/data/create_db.sql``. That repo was purged from the
working tree (it carried an e-invoice certificate; see the repo-rename /
secret-purge note) and survives only as a local archive, so the schema is
now embedded below as ``_LEGACY_DDL`` — copied VERBATIM from that
``create_db.sql`` (schema-only; no rows, no secrets). Embedding keeps the
fixture buildable anywhere, including CI, which has no legacy checkout.

The file lives at ``api/tests/fixtures/legacy_tiny.db`` and is committed
to the repo so CI does not need to regenerate it. Re-run this script
whenever the embedded DDL or seed rows change:

    cd api && uv run python tests/fixtures/build_legacy_tiny.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path


FIXTURE_PATH = Path(__file__).resolve().parent / "legacy_tiny.db"

# Legacy schema, embedded VERBATIM from the (now-archived) legacy repo's
# ``account-book-API/data/create_db.sql``. That repo was purged from the
# working tree (it carried an e-invoice certificate; see the repo-rename /
# secret-purge note) and survives only as a local archive, so the schema is
# pinned here to keep this fixture buildable anywhere — including CI, which
# has no legacy checkout. ``Initial_Setting`` is commented out in the source
# DDL, so its CREATE lives separately in ``INITIAL_SETTING_DDL`` (to exercise
# the migrator's skip path). ``carrier_no`` on Account/Credit_Card and the
# denormalized ``code_group``/``code_group_name`` columns are retained so the
# migrator's drop/normalize paths stay under test. The DDL is schema-only
# (no rows, no secrets).
_LEGACY_DDL = """
-- 帳戶設定檔
CREATE TABLE IF NOT EXISTS Account (
	id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
	account_id NVARCHAR(20),
	name NVARCHAR(60) NOT NULL,
	account_type VARCHAR(10) NOT NULL,
	fx_code CHARACTER(3) NOT NULL, -- 對應 FX_Rate.code
    is_calculate CHARACTER(1) NOT NULL,
	in_use CHARACTER(1) NOT NULL,
	discount DECIMAL(4,3), -- 最多總共四位，小數點三位
	memo NVARCHAR(300), -- 活存利率等
	owner NVARCHAR(60),
	carrier_no NVARCHAR(60),
	account_index TINYINT
);

-- 餘額檔，關帳後寫入
CREATE TABLE IF NOT EXISTS Account_Balance (
	vesting_month CHARACTER(6) NOT NULL,
	id NVARCHAR(20),
	name NVARCHAR(60) NOT NULL,
    balance DECIMAL(9,2) NOT NULL,
	fx_code CHARACTER(3) NOT NULL,
	fx_rate DECIMAL(5,2) NOT NULL,
	is_calculate CHARACTER(1) NOT NULL,
	PRIMARY KEY (vesting_month, id)
);

-- 定期支出提醒設定檔
CREATE TABLE IF NOT EXISTS Alarm (
    alarm_id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
	alarm_type VARCHAR(10) NOT NULL,
	alarm_date VARCHAR(5) NOT NULL,
    content NVARCHAR(60) NOT NULL,
	due_date DATE
);

-- 預算設定檔
CREATE TABLE IF NOT EXISTS Budget (
	budget_year CHARACTER(4),
	category_code VARCHAR(10), --對應 Code_Data.code_id
	category_name NVARCHAR(60) NOT NULL, -- 對應 Code_Data.name
	code_type VARCHAR(10) NOT NULL, -- 對應 Code_Data.code_type
    expected01 DECIMAL(9,2) NOT NULL,
	expected02 DECIMAL(9,2) NOT NULL,
	expected03 DECIMAL(9,2) NOT NULL,
	expected04 DECIMAL(9,2) NOT NULL,
	expected05 DECIMAL(9,2) NOT NULL,
	expected06 DECIMAL(9,2) NOT NULL,
	expected07 DECIMAL(9,2) NOT NULL,
	expected08 DECIMAL(9,2) NOT NULL,
	expected09 DECIMAL(9,2) NOT NULL,
	expected10 DECIMAL(9,2) NOT NULL,
	expected11 DECIMAL(9,2) NOT NULL,
	expected12 DECIMAL(9,2) NOT NULL,
	PRIMARY KEY (budget_year, category_code)
);

-- 代碼檔
CREATE TABLE IF NOT EXISTS Code_Data (
	code_id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
	code_type VARCHAR(10) NOT NULL, --S：固定支出/ F：浮動支出/ I：收入/ A：資產
	name NVARCHAR(60) NOT NULL,
	code_group INTEGER, --如果是副選單，會寫入Code_Data.code_id
	code_group_name NVARCHAR(60), --如果是副選單，會寫入Code_Data.name
	in_use CHARACTER(1) NOT NULL,
    code_index TINYINT
);

-- 信用卡設定檔
CREATE TABLE IF NOT EXISTS Credit_Card (
	credit_card_id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
	card_name NVARCHAR(60) NOT NULL,
	card_no NVARCHAR(19) NOT NULL,
	last_day CHARACTER(2) NOT NULL,
    charge_day CHARACTER(2) NOT NULL,
	limit_date NVARCHAR(7) NOT NULL,
    feedback_way NVARCHAR(5) NOT NULL, --Cash：現金/ Point：紅利/ None：無
	fx_code CHARACTER(3) NOT NULL, -- 對應 FX_Rate.code
	in_use CHARACTER(1) NOT NULL,
	credit_card_index TINYINT,
	carrier_no NVARCHAR(60),
    note TEXT -- 記錄額度，優惠到期日，回饋上限金額之類的
);

-- 可計算當月解約金的保險每月價值檔，關帳後寫入
CREATE TABLE IF NOT EXISTS Credit_Card_Balance (
	vesting_month CHARACTER(6) NOT NULL,
	id INTEGER,
	name NVARCHAR(60) NOT NULL,
    balance DECIMAL(9,2) NOT NULL,
	fx_rate DECIMAL(5,2) NOT NULL,
	PRIMARY KEY (vesting_month, id)
);

-- 不動產主檔
CREATE TABLE IF NOT EXISTS Estate (
	estate_id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
	estate_name NVARCHAR(60) NOT NULL,
	estate_type VARCHAR(10) NOT NULL, -- house:獨棟透天 / townhouse:連棟透天 / condo:公寓 / apartment:電梯大樓 / highrise:商辦 / land:土地
	estate_address NVARCHAR(300) NOT NULL,
	asset_id INTEGER NOT NULL,
	obtain_date DATE NOT NULL,
	loan_id INTEGER, -- 對應 Loan.loan_id
	estate_status VARCHAR(10) NOT NULL, -- idle:閒置 / live:居住 / rent:出租 / sold:賣出
	memo NVARCHAR(300) -- 寫坪數/建造日/總樓高/有什麼車位/格局/有無管理
);
CREATE INDEX IF NOT EXISTS Estate_idx ON Estate (estate_id, asset_id);

-- 不動產流水帳檔
CREATE TABLE IF NOT EXISTS Estate_Journal (
	distinct_number INTEGER PRIMARY KEY ASC AUTOINCREMENT,
	estate_id INTEGER NOT NULL,
	estate_excute_type VARCHAR(20) NOT NULL, -- tax:稅費 / fee:雜費 / insurance:保險 / fix:修繕 / rent:租金 / deposit:押金
	excute_price DECIMAL(9,2) NOT NULL,
	excute_date DATE NOT NULL,
	memo NVARCHAR(300)
);
CREATE INDEX IF NOT EXISTS Estate_Journal_idx ON Estate_Journal (estate_id, excute_date);
CREATE INDEX IF NOT EXISTS Estate_Income_idx ON Estate_Journal (estate_id, estate_excute_type);

-- 可計算當月解約金的保險每月價值檔，關帳後寫入
CREATE TABLE IF NOT EXISTS Estate_Net_Value_History (
	vesting_month CHARACTER(6) NOT NULL,
	id INTEGER, -- Estate.estate_id
	name NVARCHAR(60) NOT NULL,
	asset_id INTEGER NOT NULL, -- Estate.asset_id
	market_value DECIMAL(9,2) NOT NULL, -- 從估價網站輸入對等條件取值填入
	cost DECIMAL(9,2) NOT NULL, -- 會算入所有支出收入，為計算當下報酬率
	estate_status VARCHAR(10) NOT NULL,
	PRIMARY KEY (vesting_month, id, asset_id)
);

-- 歷史匯率檔，當天有撈才會寫入
CREATE TABLE IF NOT EXISTS FX_Rate (
	import_date DATETIME,
	code CHARACTER(3),
	buy_rate DECIMAL(5,2) NOT NULL,
	PRIMARY KEY (import_date, code)
);

-- 保險流水帳檔
CREATE TABLE IF NOT EXISTS Insurance (
	insurance_id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
	insurance_name NVARCHAR(60) NOT NULL,
	asset_id INTEGER NOT NULL,
	in_account_id INTEGER NOT NULL,
    in_account_name NVARCHAR(60) NOT NULL,
	out_account_id INTEGER NOT NULL,
    out_account_name NVARCHAR(60) NOT NULL,
	start_date DATE NOT NULL,
	expected_end_date DATE NOT NULL,
	pay_type VARCHAR(10) NOT NULL, -- 繳別，month:月/ season:季/ year:年/ once:躉繳
    pay_day VARCHAR(23), -- 依繳別，month:dd/ season:mm/dd,mm/dd.../ year:mm/dd
	expected_spend INTEGER NOT NULL,
	has_closed CHARACTER(1) NOT NULL
);

-- 保險明細檔
CREATE TABLE IF NOT EXISTS Insurance_Journal (
	distinct_number INTEGER PRIMARY KEY ASC AUTOINCREMENT,
	insurance_id INTEGER NOT NULL,
	insurance_excute_type VARCHAR(20) NOT NULL, -- pay:扣款/ cash:配息/ return:贖回/ expect:預期價值
	excute_price DECIMAL(7,3) NOT NULL,
	excute_date DATE NOT NULL,
	memo NVARCHAR(300)
);
CREATE INDEX IF NOT EXISTS Insurance_Journal_idx ON Insurance_Journal (insurance_id, excute_date);
CREATE INDEX IF NOT EXISTS Insurance_Income_idx ON Insurance_Journal (insurance_id, insurance_excute_type);

-- 可計算當月解約金的保險每月價值檔，關帳後寫入
CREATE TABLE IF NOT EXISTS Insurance_Net_Value_History (
	vesting_month CHARACTER(6) NOT NULL,
	id INTEGER, -- Insurance.insurance_id
	name NVARCHAR(60) NOT NULL,
	asset_id INTEGER NOT NULL, -- Insurance.asset_id
	surrender_value DECIMAL(9,2) NOT NULL, -- 當年度解約金或預期價值，一個月只能有一筆
	cost DECIMAL(9,2) NOT NULL, -- 會算入配息與所有支出，為計算當下報酬率
	fx_code CHARACTER(3) NOT NULL,
	fx_rate DECIMAL(5,2) NOT NULL,
	PRIMARY KEY (vesting_month, id, asset_id)
);

-- 流水帳檔
CREATE TABLE IF NOT EXISTS Journal (
	distinct_number INTEGER PRIMARY KEY ASC AUTOINCREMENT,
	vesting_month CHARACTER(6) NOT NULL,
	spend_date DATE NOT NULL,
	spend_way VARCHAR(10) NOT NULL, -- account_id / credit_card_id
	spend_way_type VARCHAR(20) NOT NULL,
	spend_way_table VARCHAR(15) NOT NULL, -- id 對應的 table
	action_main VARCHAR(10) NOT NULL,
	action_main_type VARCHAR(20) NOT NULL,
	action_main_table VARCHAR(15) NOT NULL,
    action_sub VARCHAR(10) NOT NULL,
	action_sub_type VARCHAR(20) NOT NULL,
	action_sub_table VARCHAR(15) NOT NULL, -- id 對應的 table
    spending DECIMAL(9,2) NOT NULL, -- 收入為正，支出為負
	invoice_number CHAR(10), -- 有填發票號碼為匯入資料，用來判斷是否要寫入新的匯入資料
    note TEXT
);
CREATE INDEX IF NOT EXISTS Journal_spend_date_idx ON Journal (spend_date);

-- 貸款主檔
CREATE TABLE IF NOT EXISTS Loan (
	loan_id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
	loan_name NVARCHAR(60) NOT NULL,
	loan_type VARCHAR(10) NOT NULL, -- unsecured:信貸 / mortgage:房貸 / financial:理財型房貸 / secured:擔保貸款
	account_id INTEGER NOT NULL, -- 對應 Account.account_id
    account_name NVARCHAR(60) NOT NULL, -- 對應 Account.name
	interest_rate DECIMAL(4,3) NOT NULL,
	period INTEGER NOT NULL,
	apply_date DATE NOT NULL,
	grace_expire_date DATE,
	pay_day VARCHAR(2) NOT NULL,
	amount DECIMAL(9,2) NOT NULL,
	repayed CHARACTER(1) NOT NULL,
	loan_index TINYINT
);

-- 貸款流水帳檔
CREATE TABLE IF NOT EXISTS Loan_Journal (
	distinct_number INTEGER PRIMARY KEY ASC AUTOINCREMENT,
	loan_id INTEGER NOT NULL,
	loan_excute_type VARCHAR(20) NOT NULL, -- principal:償還本金 / interest:支付利息 / increment:增貸 / fee:雜費
	excute_price DECIMAL(9,2) NOT NULL,
	excute_date DATE NOT NULL,
	memo NVARCHAR(300)
);
CREATE INDEX IF NOT EXISTS Loan_Journal_idx ON Loan_Journal (loan_id, excute_date);
CREATE INDEX IF NOT EXISTS Loan_Income_idx ON Loan_Journal (loan_id, Loan_excute_type);

-- 貸款餘額檔，關帳後寫入
CREATE TABLE IF NOT EXISTS Loan_Balance (
	vesting_month CHARACTER(6) NOT NULL,
	id INTEGER,
	name NVARCHAR(60) NOT NULL,
    balance DECIMAL(9,2) NOT NULL,
	cost DECIMAL(9,2) NOT NULL, -- 會算入繳息與所有支出，為計算當下總成本
	PRIMARY KEY (vesting_month, id)
);

-- 其他資產設定檔
CREATE TABLE IF NOT EXISTS Other_Asset (
    asset_id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
	asset_name NVARCHAR(60) NOT NULL,
	asset_type VARCHAR(10) NOT NULL,
	vesting_nation VARCHAR(10),
	in_use CHARACTER(1) NOT NULL,
	asset_index TINYINT
);

-- 股票流水帳檔 (尚未賣出都可以做在同一包)
CREATE TABLE IF NOT EXISTS Stock_Journal (
	stock_id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
	stock_code VARCHAR(10) NOT NULL,
	stock_name NVARCHAR(60) NOT NULL,
	asset_id INTEGER NOT NULL,
	expected_spend INTEGER
);

-- 股票明細檔
CREATE TABLE IF NOT EXISTS Stock_Detail (
	distinct_number INTEGER PRIMARY KEY ASC AUTOINCREMENT,
	stock_id INTEGER NOT NULL,
	excute_type VARCHAR(20) NOT NULL, -- buy:買入/ sell:賣出/ stock:配股/ cash:配息
	excute_amount DECIMAL(7,5), --以股為單位
	excute_price DECIMAL(9,3),
	excute_date DATE NOT NULL,
	account_id INTEGER NOT NULL,
    account_name NVARCHAR(60) NOT NULL,
	memo NVARCHAR(300)
);
CREATE INDEX IF NOT EXISTS Stock_Detail_idx ON Stock_Detail (stock_id, excute_date);

-- 股票每月淨值檔，關帳後寫入
CREATE TABLE IF NOT EXISTS Stock_Net_Value_History (
	vesting_month CHARACTER(6) NOT NULL,
	id INTEGER, -- Stock_Journal.stock_id
	stock_code VARCHAR(10) NOT NULL,
	stock_name NVARCHAR(60) NOT NULL,
	asset_id INTEGER NOT NULL,
	amount DECIMAL(7,5) NOT NULL,
	price DECIMAL(7,3) NOT NULL,
	cost DECIMAL(9,2) NOT NULL, -- 會算入配息，為計算當下報酬率
	fx_code CHARACTER(3) NOT NULL,
	fx_rate DECIMAL(5,2) NOT NULL,
	PRIMARY KEY (vesting_month, id, asset_id)
);

-- 股票歷史價格檔
CREATE TABLE IF NOT EXISTS Stock_Price_History (
	stock_code VARCHAR(10) NOT NULL,
	fetch_date DATETIME NOT NULL,
	open_price DECIMAL(7,3),
	highest_price DECIMAL(7,3),
	lowest_price DECIMAL(7,3),
	close_price DECIMAL(7,3) NOT NULL,
	PRIMARY KEY (stock_code, fetch_date)
);

-- 年度目標設定檔
CREATE TABLE IF NOT EXISTS Target_Setting (
	distinct_number INTEGER PRIMARY KEY ASC AUTOINCREMENT,
	target_year CHARACTER(4) NOT NULL,
	setting_value NVARCHAR(45) NOT NULL, -- 描述該年度目標
	is_done CHARACTER(1) NOT NULL
);
"""

INITIAL_SETTING_DDL = """
CREATE TABLE IF NOT EXISTS Initial_Setting (
    id INTEGER PRIMARY KEY,
    code_table VARCHAR(15) NOT NULL,
    code_name NVARCHAR(60) NOT NULL,
    initial_type VARCHAR(10) NOT NULL,
    setting_value VARCHAR(10) NOT NULL,
    setting_date DATE NOT NULL
);
"""


def _build_schema(conn: sqlite3.Connection) -> None:
    """Execute the embedded legacy DDL + an explicit Initial_Setting CREATE."""
    conn.executescript(_LEGACY_DDL)
    conn.executescript(INITIAL_SETTING_DDL)


def _insert_account(conn: sqlite3.Connection) -> None:
    rows = [
        # Row 1: carrier_no set — proves the drop path.
        (1, "FAKE-ACCT-01", "Fake Bank", "bank", "USD", "Y", "Y", 1.0,
         "Fake memo", "tester", "DROP-ME-1", 1),
        # Row 2: carrier_no NULL — proves the absence path.
        (2, "FAKE-ACCT-02", "Fake Cash", "cash", "TWD", "Y", "Y", 1.0,
         None, None, None, 2),
    ]
    conn.executemany(
        "INSERT INTO Account (id, account_id, name, account_type, fx_code, "
        "is_calculate, in_use, discount, memo, owner, carrier_no, account_index) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )


def _insert_code_data(conn: sqlite3.Connection) -> None:
    rows = [
        (1, "Floating", "Food", None, None, "Y", 1),
        (2, "Income", "Salary", None, None, "Y", 2),
    ]
    conn.executemany(
        "INSERT INTO Code_Data (code_id, code_type, name, code_group, "
        "code_group_name, in_use, code_index) VALUES (?, ?, ?, ?, ?, ?, ?)",
        rows,
    )


def _insert_credit_card(conn: sqlite3.Connection) -> None:
    rows = [
        # Row 1: carrier_no set; limit_date in the common 'YYYY/MM' shape.
        (1, "Fake Visa", "4111-XXXX-XXXX-1111", "25", "15", "2026/08", "Cash",
         "USD", "Y", 1, "DROP-CC-1", "primary"),
        # Row 2: carrier_no NULL; limit_date as a datetime string (real
        # legacy rows hold both shapes).
        (2, "Fake Master", "5500-XXXX-XXXX-2222", "20", "10",
         "2022-07-30 16:00:00.000000", "Point", "TWD", "Y", 2, None, None),
    ]
    conn.executemany(
        "INSERT INTO Credit_Card (credit_card_id, card_name, card_no, last_day, "
        "charge_day, limit_date, feedback_way, fx_code, in_use, "
        "credit_card_index, carrier_no, note) VALUES "
        "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )


def _insert_budget(conn: sqlite3.Connection) -> None:
    months_cols = ", ".join(f"expected{m:02d}" for m in range(1, 13))
    placeholders = ", ".join("?" for _ in range(16))
    rows = [
        ("2024", "1", "Food", "Floating", *([1000.0] * 12)),
        ("2024", "2", "Salary", "Income", *([2000.0] * 12)),
    ]
    conn.executemany(
        f"INSERT INTO Budget (budget_year, category_code, category_name, code_type, "
        f"{months_cols}) VALUES ({placeholders})",
        rows,
    )


def _insert_alarm(conn: sqlite3.Connection) -> None:
    rows = [
        # Real legacy shape: 'MM/DD' anchor + datetime-string due_date.
        (1, "Y", "05/31", "報稅", "2022-07-30 16:00:00.000000"),
        (2, "M", "06/15", "Monthly bill", None),
    ]
    conn.executemany(
        "INSERT INTO Alarm (alarm_id, alarm_type, alarm_date, content, due_date) "
        "VALUES (?, ?, ?, ?, ?)",
        rows,
    )


def _insert_other_asset(conn: sqlite3.Connection) -> None:
    rows = [
        (1, "Fake Stock Bucket", "stock", "US", "Y", 1),
        (2, "Fake Estate Bucket", "estate", "TW", "Y", 2),
    ]
    conn.executemany(
        "INSERT INTO Other_Asset (asset_id, asset_name, asset_type, "
        "vesting_nation, in_use, asset_index) VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )


def _insert_loan(conn: sqlite3.Connection) -> None:
    rows = [
        # account_id = 1 references Account.id = 1 (FAKE-ACCT-01).
        # interest_rate uses the legacy percent form (1.31 = 1.31%).
        (1, "Fake Mortgage", "mortgage", 1, "Fake Bank", 1.31, 360,
         "2020-01-01", "2020-04-01", "01", 250000.0, "N", 1),
        (2, "Fake Auto", "unsecured", 2, "Fake Cash", 2.5, 60,
         "2023-03-01", None, "10", 20000.0, "N", 2),
    ]
    conn.executemany(
        "INSERT INTO Loan (loan_id, loan_name, loan_type, account_id, "
        "account_name, interest_rate, period, apply_date, grace_expire_date, "
        "pay_day, amount, repayed, loan_index) VALUES "
        "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )


def _insert_loan_journal(conn: sqlite3.Connection) -> None:
    rows = [
        # IMPL-NOTE: legacy ledger.db stores principal rows as a NEGATIVE
        # excute_price; the migrator must abs() it to the canonical positive
        # magnitude (see test_loan_journal_principal_sign_normalized).
        (1, 1, "principal", -1500.0, "2025-01-15", "Jan principal"),
        (2, 1, "interest", 600.0, "2025-01-15", "Jan interest"),
    ]
    conn.executemany(
        "INSERT INTO Loan_Journal (distinct_number, loan_id, loan_excute_type, "
        "excute_price, excute_date, memo) VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )


def _insert_loan_balance(conn: sqlite3.Connection) -> None:
    rows = [
        ("202604", 1, "Fake Mortgage", -240000.0, 250000.0),
        ("202604", 2, "Fake Auto", -18000.0, 20000.0),
    ]
    conn.executemany(
        "INSERT INTO Loan_Balance (vesting_month, id, name, balance, cost) "
        "VALUES (?, ?, ?, ?, ?)",
        rows,
    )


def _insert_stock_journal(conn: sqlite3.Connection) -> None:
    rows = [
        (1, "AAPL", "Apple Inc.", 1, 10000),
        (2, "2330.TW", "TSMC", 1, 80000),
    ]
    conn.executemany(
        "INSERT INTO Stock_Journal (stock_id, stock_code, stock_name, "
        "asset_id, expected_spend) VALUES (?, ?, ?, ?, ?)",
        rows,
    )


def _insert_stock_detail(conn: sqlite3.Connection) -> None:
    rows = [
        # account_id = 1 → FAKE-ACCT-01
        (1, 1, "buy", 10.0, 180.5, "2024-01-15", 1, "Fake Bank", "Initial buy"),
        (2, 2, "buy", 100.0, 800.0, "2024-02-20", 1, "Fake Bank", "TSMC buy"),
    ]
    conn.executemany(
        "INSERT INTO Stock_Detail (distinct_number, stock_id, excute_type, "
        "excute_amount, excute_price, excute_date, account_id, account_name, memo) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )


def _insert_stock_net_value_history(conn: sqlite3.Connection) -> None:
    rows = [
        ("202604", 1, "AAPL", "Apple Inc.", 1, 10.0, 185.0, 1850.0, "USD", 31.5),
        ("202604", 2, "2330.TW", "TSMC", 1, 100.0, 850.0, 80000.0, "TWD", 1.0),
    ]
    conn.executemany(
        "INSERT INTO Stock_Net_Value_History (vesting_month, id, stock_code, "
        "stock_name, asset_id, amount, price, cost, fx_code, fx_rate) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )


def _insert_insurance(conn: sqlite3.Connection) -> None:
    rows = [
        # in_account_id=1, out_account_id=1 → FAKE-ACCT-01.
        # pay_type uses legacy cadence words ('year'/'month') to exercise
        # the annual/monthly remap.
        (1, "Fake Whole Life", 1, 1, "Fake Bank", 1, "Fake Bank",
         "2020-01-01", "2050-01-01", "year", "01/15", 1200, "N"),
        (2, "Fake Term Life", 1, 2, "Fake Cash", 2, "Fake Cash",
         "2010-01-01", "2024-01-01", "month", "20", 800, "Y"),
    ]
    conn.executemany(
        "INSERT INTO Insurance (insurance_id, insurance_name, asset_id, "
        "in_account_id, in_account_name, out_account_id, out_account_name, "
        "start_date, expected_end_date, pay_type, pay_day, expected_spend, "
        "has_closed) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )


def _insert_insurance_journal(conn: sqlite3.Connection) -> None:
    rows = [
        (1, 1, "pay", 1200.0, "2025-01-15", "2025 premium"),
        (2, 1, "pay", 1200.0, "2026-01-15", "2026 premium"),
        # 'expect' (預期價值) rows divert to Insurance_Value_History.
        (3, 1, "expect", 26000.0, "2026-02-01", "預期價值"),
    ]
    conn.executemany(
        "INSERT INTO Insurance_Journal (distinct_number, insurance_id, "
        "insurance_excute_type, excute_price, excute_date, memo) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )


def _insert_insurance_net_value_history(conn: sqlite3.Connection) -> None:
    rows = [
        ("202604", 1, "Fake Whole Life", 1, 25000.0, 20000.0, "USD", 31.5),
        ("202604", 2, "Fake Term Life", 1, 8000.0, 7000.0, "USD", 31.5),
    ]
    conn.executemany(
        "INSERT INTO Insurance_Net_Value_History (vesting_month, id, name, "
        "asset_id, surrender_value, cost, fx_code, fx_rate) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )


def _insert_estate(conn: sqlite3.Connection) -> None:
    rows = [
        (1, "Fake Condo", "condo", "123 Fake St", 2, "2020-01-01", 1, "live",
         "Primary residence"),
        (2, "Fake Land", "land", "456 Fake Rd", 2, "2021-06-01", None, "idle",
         None),
    ]
    conn.executemany(
        "INSERT INTO Estate (estate_id, estate_name, estate_type, estate_address, "
        "asset_id, obtain_date, loan_id, estate_status, memo) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )


def _insert_estate_journal(conn: sqlite3.Connection) -> None:
    rows = [
        (1, 1, "tax", 5000.0, "2025-01-01", "Property tax"),
        (2, 1, "fix", 2500.0, "2025-06-01", "Maintenance"),
        # Two same-month 'marketValue' appraisal rows divert to
        # Estate_Value_History; the later excute_date must win.
        (3, 1, "marketValue", 480000.0, "2025-03-10", "older appraisal"),
        (4, 1, "marketValue", 500000.0, "2025-03-20", "newer appraisal"),
    ]
    conn.executemany(
        "INSERT INTO Estate_Journal (distinct_number, estate_id, "
        "estate_excute_type, excute_price, excute_date, memo) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )


def _insert_estate_net_value_history(conn: sqlite3.Connection) -> None:
    rows = [
        ("202604", 1, "Fake Condo", 2, 500000.0, 420000.0, "live"),
        ("202604", 2, "Fake Land", 2, 200000.0, 180000.0, "idle"),
    ]
    conn.executemany(
        "INSERT INTO Estate_Net_Value_History (vesting_month, id, name, "
        "asset_id, market_value, cost, estate_status) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        rows,
    )


def _insert_journal(conn: sqlite3.Connection) -> None:
    rows = [
        (1, "202604", "2026-04-18", "FAKE-ACCT-01", "account", "Account",
         "1", "Floating", "Code_Data", "", "", "", -123.45,
         "AB12345678", "Lunch"),
        # Real legacy rows capitalize the credit-card discriminator.
        (2, "202604", "2026-04-19", "1", "Credit_Card", "Credit_Card",
         "2", "Income", "Code_Data", "", "", "", 5000.0,
         None, "Pay day"),
    ]
    conn.executemany(
        "INSERT INTO Journal (distinct_number, vesting_month, spend_date, "
        "spend_way, spend_way_type, spend_way_table, action_main, "
        "action_main_type, action_main_table, action_sub, action_sub_type, "
        "action_sub_table, spending, invoice_number, note) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )


def _insert_account_balance(conn: sqlite3.Connection) -> None:
    rows = [
        ("202604", "FAKE-ACCT-01", "Fake Bank", 10000.0, "USD", 31.5, "Y"),
        ("202604", "FAKE-ACCT-02", "Fake Cash", 500.0, "TWD", 1.0, "Y"),
    ]
    conn.executemany(
        "INSERT INTO Account_Balance (vesting_month, id, name, balance, "
        "fx_code, fx_rate, is_calculate) VALUES (?, ?, ?, ?, ?, ?, ?)",
        rows,
    )


def _insert_credit_card_balance(conn: sqlite3.Connection) -> None:
    rows = [
        ("202604", 1, "Fake Visa", -2500.0, 31.5),
        ("202604", 2, "Fake Master", -1500.0, 1.0),
    ]
    conn.executemany(
        "INSERT INTO Credit_Card_Balance (vesting_month, id, name, balance, "
        "fx_rate) VALUES (?, ?, ?, ?, ?)",
        rows,
    )


def _insert_fx_rate(conn: sqlite3.Connection) -> None:
    rows = [
        ("2026-04-18 00:00:00", "USD", 31.52),
        ("2026-04-18 00:00:00", "TWD", 1.0),
    ]
    conn.executemany(
        "INSERT INTO FX_Rate (import_date, code, buy_rate) VALUES (?, ?, ?)",
        rows,
    )


def _insert_stock_price_history(conn: sqlite3.Connection) -> None:
    rows = [
        ("AAPL", "2026-04-18 00:00:00", 180.0, 182.5, 179.2, 181.8),
        ("2330.TW", "2026-04-18 00:00:00", 800.0, 810.0, 795.0, 805.0),
    ]
    conn.executemany(
        "INSERT INTO Stock_Price_History (stock_code, fetch_date, open_price, "
        "highest_price, lowest_price, close_price) VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )


def _insert_target_setting(conn: sqlite3.Connection) -> None:
    rows = [
        (1, "2026", "1000000", "N"),
        (2, "2027", "1200000", "N"),
    ]
    conn.executemany(
        "INSERT INTO Target_Setting (distinct_number, target_year, "
        "setting_value, is_done) VALUES (?, ?, ?, ?)",
        rows,
    )


def _insert_initial_setting(conn: sqlite3.Connection) -> None:
    """One row that should be skipped by the migrator."""
    conn.execute(
        "INSERT INTO Initial_Setting (id, code_table, code_name, initial_type, "
        "setting_value, setting_date) VALUES (?, ?, ?, ?, ?, ?)",
        (1, "Account", "Should be skipped", "balance", "0", "2020-01-01"),
    )


# Per-table inserters in FK-creation order. Most tables get exactly 2 rows;
# Insurance_Journal carries a 3rd ('expect') and Estate_Journal a 3rd/4th
# ('marketValue') row to exercise the value-history diversion.
# ``Initial_Setting`` is included so the migrator's skip path is exercised.
INSERTERS = [
    ("Code_Data", _insert_code_data),
    ("Account", _insert_account),
    ("Credit_Card", _insert_credit_card),
    ("Budget", _insert_budget),
    ("Alarm", _insert_alarm),
    ("Other_Asset", _insert_other_asset),
    ("Loan", _insert_loan),
    ("Loan_Journal", _insert_loan_journal),
    ("Loan_Balance", _insert_loan_balance),
    ("Stock_Journal", _insert_stock_journal),
    ("Stock_Detail", _insert_stock_detail),
    ("Stock_Net_Value_History", _insert_stock_net_value_history),
    ("Insurance", _insert_insurance),
    ("Insurance_Journal", _insert_insurance_journal),
    ("Insurance_Net_Value_History", _insert_insurance_net_value_history),
    ("Estate", _insert_estate),
    ("Estate_Journal", _insert_estate_journal),
    ("Estate_Net_Value_History", _insert_estate_net_value_history),
    ("Journal", _insert_journal),
    ("Account_Balance", _insert_account_balance),
    ("Credit_Card_Balance", _insert_credit_card_balance),
    ("FX_Rate", _insert_fx_rate),
    ("Stock_Price_History", _insert_stock_price_history),
    ("Target_Setting", _insert_target_setting),
    ("Initial_Setting", _insert_initial_setting),
]


def build(path: Path = FIXTURE_PATH) -> Path:
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(path)
    try:
        _build_schema(conn)
        for _table, fn in INSERTERS:
            fn(conn)
        conn.commit()
    finally:
        conn.close()
    return path


def main() -> None:
    out = build()
    print(f"Wrote fixture: {out}")


if __name__ == "__main__":
    main()
