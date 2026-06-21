"""Shared expense/income aggregation: per-category net, then floor at 0.

Centralizes the spending-aggregation rule used across the reports, monthly, and
dashboard domains. The old per-row ``abs(spending)`` summation was wrong twice:

* A mis-typed **inflow** counted as expense — e.g. a ``+300000`` "received cash"
  row filed under an expense-type category became ``+300000`` of expense.
* **代買 (proxy-buy)** reimbursements never offset the original outflow — pay
  ``-1000`` then get ``+1000`` back in the same category summed to ``2000``.

The rule here nets each category's signed cash flow first, then floors at 0
**per category, before** summing across categories. So a net-inflow category
neither shows as expense (``max(0, -net)`` = 0) nor cancels another category's
real expense (the floor happens before the cross-category sum). Income is the
mirror image (``max(0, +net)``).

The helper itself is currency-agnostic and side-agnostic: callers pass an
``amount_of`` closure (normally ``journal_amount_twd``) for the signed amount and
classify each category's side via its returned ``action_main_type``.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable

from app.models.monthly_report.journal import Journal


def category_net_by_bucket(
    journals: Iterable[Journal],
    bucket_of: Callable[[Journal], str],
    amount_of: Callable[[Journal], float],
) -> tuple[dict[tuple[str, str], float], dict[str, str]]:
    """Signed net per ``(bucket, action_main)`` plus each category's type.

    ``bucket_of`` maps a journal to its period key — a month, a year, or a
    constant (e.g. ``""``) when the caller wants a single whole-window bucket.
    ``amount_of`` returns the signed amount to accumulate (e.g. FX-converted
    ``journal.spending``). The second return value maps ``action_main`` → the raw
    ``action_main_type`` seen on its rows, so callers can decide each category's
    side (expense / income / excluded) without a second pass over the journals.
    """
    net: dict[tuple[str, str], float] = defaultdict(float)
    cat_type: dict[str, str] = {}
    for j in journals:
        net[(bucket_of(j), j.action_main)] += amount_of(j)
        cat_type.setdefault(j.action_main, j.action_main_type)
    return dict(net), cat_type


def floor_expense(net: float) -> float:
    """Expense magnitude of a category's signed net: the outflow, floored at 0.

    A category whose signed net is positive (more cash in than out — a reimbursed
    代買 or a mis-typed inflow) contributes 0, never a negative that would cancel
    other categories' expense.
    """
    return -net if net < 0 else 0.0


def floor_income(net: float) -> float:
    """Income magnitude of a category's signed net: the inflow, floored at 0."""
    return net if net > 0 else 0.0
