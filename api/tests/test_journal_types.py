"""Unit tests for the shared action_main_type normalization helper."""
from app.services.journal_types import (
    EXPENSE_MAIN_TYPES,
    FINANCING_MAIN_TYPES,
    INCOME_MAIN_TYPES,
    KNOWN_MAIN_TYPES,
    is_uncategorized,
    norm_type,
)


def test_norm_type_handles_none_and_empty() -> None:
    assert norm_type(None) == ""
    assert norm_type("") == ""


def test_norm_type_trims_and_lowercases() -> None:
    assert norm_type(" Invest ") == "invest"
    assert norm_type("FIXED") == "fixed"
    assert norm_type("Transfer") == "transfer"


def test_capitalized_production_values_match_after_normalization() -> None:
    # Production data capitalizes these; raw membership would miss them.
    assert "Fixed" not in EXPENSE_MAIN_TYPES
    assert norm_type("Fixed") in EXPENSE_MAIN_TYPES
    assert norm_type("Passive") in INCOME_MAIN_TYPES


def test_loan_repayment_is_known_and_report_neutral() -> None:
    # The LoanRepayment financial behavior is report-neutral (like transfer): it
    # must be a KNOWN type (so loan repayments are not flagged uncategorized) but
    # is excluded from the expense/income report buckets — its principal/interest
    # split is sourced from Loan_Journal instead.
    assert norm_type("LoanRepayment") in FINANCING_MAIN_TYPES
    assert norm_type("LoanRepayment") in KNOWN_MAIN_TYPES
    assert not is_uncategorized("LoanRepayment")
    assert FINANCING_MAIN_TYPES.isdisjoint(EXPENSE_MAIN_TYPES | INCOME_MAIN_TYPES)
