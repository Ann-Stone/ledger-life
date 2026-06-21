"""Canonical ``Journal.action_main_type`` buckets + case normalization.

The value's casing is inconsistent across the codebase and legacy data —
real production data capitalizes these values ("Invest"/"Transfer"/"Fixed"/
"Income") while seeded/imported data is lowercase. Always normalize via
:func:`norm_type` before comparing against the frozensets below; a raw
``in {"invest", "transfer"}`` check silently misses rows on real data.

These sets used to be duplicated per domain service (kept local so the
lower-level monthly domain did not import the higher-level reports domain).
This shared non-domain module is the sanctioned home — do not re-localize
copies into individual services.
"""
from __future__ import annotations

EXPENSE_MAIN_TYPES = frozenset({"fixed", "floating"})
# ``passive`` (passive income: dividends/interest/rent) is income too — the
# dashboard already counts it (Income + Passive); including it here keeps
# total_income / savings-rate consistent across the reports and cash flow.
INCOME_MAIN_TYPES = frozenset({"income", "passive"})
INVEST_MAIN_TYPES = frozenset({"invest"})
TRANSFER_MAIN_TYPES = frozenset({"transfer"})
# Financing behaviors (loan repayment): report-neutral like transfer — the cash
# outflow is real, but the principal/interest split is sourced from Loan_Journal
# (cash flow + income statement), so the main Journal row must NOT be counted as
# an expense (it would double-count) and must NOT be flagged uncategorized. The
# ``LoanRepayment`` financial behavior sets action_main_type='LoanRepayment'.
FINANCING_MAIN_TYPES = frozenset({"loanrepayment"})

# Comprehensive income statement (綜合損益表) splits INCOME_MAIN_TYPES into active
# (本業) vs passive (孳息) so dividends land in the investment section, not本業.
ACTIVE_INCOME_TYPES = frozenset({"income"})
PASSIVE_INCOME_TYPES = frozenset({"passive"})
# Realized capital-gain sub-categories, matched by Code_Data.name (names survive
# code_id re-imports; see view/src/constants/noteHints.ts). These journals are
# usually typed ``invest`` (so excluded from income/passive anyway), but the
# income-statement service excludes them by *code* before the income/expense
# netting so a 資本利得 row can never be double-counted regardless of its type.
# Confirm/extend against Code_Data for the live DB.
REALIZED_GAIN_NAMES = frozenset({"資本利得", "期貨"})


# Every bucket the reports know how to place. Anything outside this union
# (legacy 'undefined' / 'No' / '' rows from e-invoice imports the user never
# classified) is invisible to type-bucketed reports.
KNOWN_MAIN_TYPES = (
    EXPENSE_MAIN_TYPES
    | INCOME_MAIN_TYPES
    | INVEST_MAIN_TYPES
    | TRANSFER_MAIN_TYPES
    | FINANCING_MAIN_TYPES
)


def norm_type(action_main_type: str | None) -> str:
    """Lowercase/trim an action_main_type for case-insensitive comparison."""
    return (action_main_type or "").strip().lower()


def is_uncategorized(action_main_type: str | None) -> bool:
    """True when the type falls outside every report bucket.

    This is the single backend definition of "uncategorized"; the frontend
    mirrors it in ``view/src/utils/journalTypes.ts`` — keep them in sync.
    """
    return norm_type(action_main_type) not in KNOWN_MAIN_TYPES
