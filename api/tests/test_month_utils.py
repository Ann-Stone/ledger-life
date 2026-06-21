"""Unit tests for the shared YYYYMM month-arithmetic helpers."""
from app.services.month_utils import (
    iter_months,
    month_end,
    month_start,
    previous_month,
    shift_month,
)


def test_month_end_is_lexicographic_sentinel() -> None:
    # "31" even for short months — callers compare YYYYMMDD strings.
    assert month_end("202602") == "20260231"
    assert month_end("202604") == "20260431"
    assert "20260228" <= month_end("202602")


def test_month_start() -> None:
    assert month_start("202601") == "20260101"


def test_shift_month_forward_and_back() -> None:
    assert shift_month("202606", 0) == "202606"
    assert shift_month("202606", 1) == "202607"
    assert shift_month("202612", 1) == "202701"
    assert shift_month("202601", -1) == "202512"
    assert shift_month("202606", 13) == "202707"
    assert shift_month("202606", -13) == "202505"


def test_previous_month_equals_shift_minus_one() -> None:
    for yyyymm in ("202601", "202612", "202507", "100001"):
        assert previous_month(yyyymm) == shift_month(yyyymm, -1)
    assert previous_month("202601") == "202512"


def test_iter_months_inclusive() -> None:
    assert iter_months("202604", "202604") == ["202604"]
    assert iter_months("202611", "202702") == ["202611", "202612", "202701", "202702"]
    assert iter_months("202605", "202604") == []
