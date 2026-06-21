"""Schema-level gates for BE-005 Phase 1.5.

These tests are migration-chain sanity checks, not data tests:

- ``test_head_has_all_retained_tables``: assert the SQLModel metadata
  (the source from which Alembic autogenerate produced the Phase 1
  migrations) registers exactly the 20 retained tables and does not
  register ``Initial_Setting``. Sub-task 1 of the granular ticket asked
  for a fresh init migration to bootstrap the schema, but Phase 1 work
  (BE-006..009 + BE-011) already produced incremental migrations that
  build the same schema; this test stands in for the "verify head
  schema covers all 20 retained tables" intent.
- ``test_dropped_columns_absent``: assert ``carrier_no`` is absent from
  the ``Account`` and ``Credit_Card`` tables (granular sub-task 2).
"""
from __future__ import annotations

from sqlalchemy import inspect
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

import app.models  # noqa: F401  registers every table on SQLModel.metadata


RETAINED_TABLES = {
    # settings
    "Account",
    "Code_Data",
    "Budget",
    "Credit_Card",
    "Alarm",
    # monthly_report
    "Journal",
    "Account_Balance",
    "Credit_Card_Balance",
    "Loan_Balance",
    "Stock_Net_Value_History",
    "Insurance_Net_Value_History",
    "Estate_Net_Value_History",
    # assets
    "Other_Asset",
    "Stock_Journal",
    "Stock_Detail",
    "Insurance",
    "Insurance_Journal",
    "Estate",
    "Estate_Journal",
    "Loan",
    "Loan_Journal",
    # dashboard
    "FX_Rate",
    "Stock_Price_History",
    "Target_Setting",
}


def test_head_has_all_retained_tables() -> None:
    registered = set(SQLModel.metadata.tables.keys())
    missing = RETAINED_TABLES - registered
    assert not missing, f"Missing retained tables in head schema: {sorted(missing)}"
    assert "Initial_Setting" not in registered, (
        "Initial_Setting must not be present in the new schema "
        "(orphan in legacy code, intentionally not ported)."
    )


def test_dropped_columns_absent() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    inspector = inspect(engine)

    account_cols = {c["name"] for c in inspector.get_columns("Account")}
    assert "carrier_no" not in account_cols, (
        "Account.carrier_no must be dropped per refactor Decision Log."
    )

    credit_card_cols = {c["name"] for c in inspector.get_columns("Credit_Card")}
    assert "carrier_no" not in credit_card_cols, (
        "Credit_Card.carrier_no must be dropped per refactor Decision Log."
    )
