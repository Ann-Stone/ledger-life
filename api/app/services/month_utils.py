"""Shared month-string arithmetic for ``YYYYMM`` vesting-month keys.

All dates in this codebase are stored and compared as plain ``YYYYMMDD``
strings, so :func:`month_end` returns the intentionally invalid-but-
lexicographically-correct sentinel ``"YYYYMM31"``: every real date in the
month sorts at or below it, regardless of how many days the month actually
has. Do NOT "fix" it to a real calendar month-end — callers rely on string
comparison windows, not calendar validity.
"""
from __future__ import annotations


def month_end(yyyymm: str) -> str:
    """Upper bound (inclusive) for ``YYYYMMDD`` comparisons within a month."""
    return f"{yyyymm}31"


def month_start(yyyymm: str) -> str:
    """First day of the month as ``YYYYMMDD``."""
    return f"{yyyymm}01"


def shift_month(yyyymm: str, delta: int) -> str:
    """Shift a ``YYYYMM`` key by ``delta`` months (negative shifts back)."""
    year = int(yyyymm[:4])
    month = int(yyyymm[4:]) + delta
    while month <= 0:
        month += 12
        year -= 1
    while month > 12:
        month -= 12
        year += 1
    return f"{year:04d}{month:02d}"


def previous_month(yyyymm: str) -> str:
    """The ``YYYYMM`` key immediately before ``yyyymm``."""
    return shift_month(yyyymm, -1)


def iter_months(start: str, end: str) -> list[str]:
    """All ``YYYYMM`` keys from ``start`` to ``end``, inclusive on both ends."""
    months: list[str] = []
    cur_year, cur_month = int(start[:4]), int(start[4:])
    end_year, end_month = int(end[:4]), int(end[4:])
    while (cur_year, cur_month) <= (end_year, end_month):
        months.append(f"{cur_year:04d}{cur_month:02d}")
        cur_month += 1
        if cur_month > 12:
            cur_month = 1
            cur_year += 1
    return months
