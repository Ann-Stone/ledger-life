"""One-off audit/fix: normalize negative ``Loan_Journal`` excute_price.

Why this exists
---------------
The legacy ``ledger.db`` (BE-005 import) stored loan ``principal`` rows as a
NEGATIVE ``excute_price`` (e.g. ``-23206.0``). The canonical convention — the
one every downstream reader assumes — is a POSITIVE magnitude for *every*
``loan_excute_type``:

* ``settlement_service.run_loan_step`` computes ``balance = amount - sum(principal)``
  and ``repayed = sum(principal)``;
* ``report_service._loanjournal_amount_twd`` documents the stored value as
  "a positive magnitude";
* ``get_cash_flow`` / ``get_income_statement`` sum the same magnitudes.

A negative principal therefore inflates the outstanding balance and corrupts
the repaid total and the income/cash-flow reports.

The root cause (the legacy migrator copying the sign verbatim) is fixed in
``scripts/migrate_from_legacy.migrate_loan_journals``, and the newer composite
endpoint ``POST /monthly-report/journals/loan-transaction`` already writes
principal POSITIVE. This script repairs DBs that were populated *before* those
fixes (e.g. ``~/.networth/networth-test.db``).

What it does
------------
1. Reports every negative-magnitude ``Loan_Journal`` row, grouped by ``loan_id``.
2. Flips each to ``abs()`` (interest/fee rows are already positive in practice,
   but abs-ing *all* loan rows is the safe canonical normalization, matching
   the migrator).
3. Re-runs ``asset_service._recalculate_repayed`` for every affected loan so
   ``Loan.repayed`` reflects the corrected principal sum.
4. Is idempotent — a second run finds nothing and changes nothing.

Usage
-----
    cd api && uv run python -m app.scripts.fix_loan_journal_signs \\
        [--target-db-url sqlite:///~/.networth/networth-test.db] [--dry-run]

The default target is ``app.config.settings.database_url``.
"""
from __future__ import annotations

import argparse
import logging
import sys
from collections import Counter
from dataclasses import dataclass, field

from sqlmodel import Session, create_engine, select

import app.models  # noqa: F401  registers tables on SQLModel.metadata
from app.config import settings as app_settings
from app.database import _resolve_sqlite_url
from app.models.assets.loan import LoanJournal
from app.services.asset_service import _recalculate_repayed

logger = logging.getLogger("fix_loan_journal_signs")


@dataclass
class FixReport:
    """Outcome of one :func:`fix_loan_journal_signs` invocation."""

    negatives_by_loan: dict[str, int] = field(default_factory=dict)
    rows_flipped: int = 0
    loans_recalculated: list[str] = field(default_factory=list)
    dry_run: bool = False

    @property
    def total_negatives(self) -> int:
        return sum(self.negatives_by_loan.values())


def fix_loan_journal_signs(session: Session, *, dry_run: bool = False) -> FixReport:
    """Flip negative ``Loan_Journal`` rows to a positive magnitude.

    Returns a :class:`FixReport`. Safe to run repeatedly: after the first run no
    negative rows remain, so a second run reports zero and mutates nothing. With
    ``dry_run=True`` the negatives are reported but nothing is written.
    """
    negatives = list(
        session.exec(select(LoanJournal).where(LoanJournal.excute_price < 0)).all()
    )

    counts = Counter(row.loan_id for row in negatives)
    report = FixReport(
        negatives_by_loan=dict(sorted(counts.items())),
        dry_run=dry_run,
    )

    for loan_id, n in report.negatives_by_loan.items():
        logger.info("loan_id=%s: %d negative Loan_Journal row(s)", loan_id, n)

    if not negatives:
        logger.info("No negative Loan_Journal rows found — nothing to fix.")
        return report

    if dry_run:
        logger.info(
            "Dry run: %d row(s) across %d loan(s) would be flipped to positive.",
            len(negatives),
            len(report.negatives_by_loan),
        )
        return report

    for row in negatives:
        row.excute_price = abs(row.excute_price)
        session.add(row)
    session.commit()
    report.rows_flipped = len(negatives)

    for loan_id in report.negatives_by_loan:
        _recalculate_repayed(session, loan_id)
        report.loans_recalculated.append(loan_id)

    logger.info(
        "Flipped %d row(s) to positive; recalculated repayed for %d loan(s).",
        report.rows_flipped,
        len(report.loans_recalculated),
    )
    return report


def main(target_db_url: str | None = None, *, dry_run: bool = False) -> FixReport:
    """Open the target SQLite DB and run :func:`fix_loan_journal_signs`."""
    url = _resolve_sqlite_url(target_db_url or app_settings.database_url)
    engine = create_engine(url, connect_args={"check_same_thread": False})
    try:
        with Session(engine) as session:
            return fix_loan_journal_signs(session, dry_run=dry_run)
    finally:
        engine.dispose()


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fix_loan_journal_signs",
        description=(
            "Normalize negative Loan_Journal excute_price (legacy stored "
            "principal NEGATIVE) to the canonical positive magnitude and "
            "recompute Loan.repayed. Idempotent."
        ),
    )
    parser.add_argument(
        "--target-db-url",
        default=None,
        help=(
            "Override the target SQLite URL. Defaults to "
            "app.config.settings.database_url."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report negative rows without writing any changes.",
    )
    return parser


def _cli_entry(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = _build_arg_parser().parse_args(argv)
    report = main(target_db_url=args.target_db_url, dry_run=args.dry_run)
    print(
        f"negative rows: {report.total_negatives} across "
        f"{len(report.negatives_by_loan)} loan(s); "
        f"flipped: {report.rows_flipped}; "
        f"recalculated: {len(report.loans_recalculated)}"
        + (" (dry run — no changes written)" if report.dry_run else "")
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(_cli_entry())
