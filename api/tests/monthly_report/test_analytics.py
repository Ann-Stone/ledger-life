"""BE-017 — Journal analytics tests."""
from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.monthly_report.analytics import (
    ExpenditureBudgetResponse,
    ExpenditureRatioResponse,
    InvestRatioResponse,
    LiabilityResponse,
)
from app.services.monthly_report_service import (
    compute_expenditure_budget,
    compute_expenditure_ratio,
    compute_invest_ratio,
    compute_liability,
)

GOLDEN_PATH = Path(__file__).resolve().parent.parent / "fixtures" / "analytics_golden.json"


def _golden() -> dict:
    return json.loads(GOLDEN_PATH.read_text())


def _normalise_items(items: list[dict], key: str = "name") -> list[dict]:
    return sorted(items, key=lambda x: x[key])


# ---- Sub-task 1-4: schemas ----


def test_expenditure_ratio_schema() -> None:
    js = ExpenditureRatioResponse.model_json_schema()
    assert "example" in js
    for n, p in js["properties"].items():
        assert "description" in p, n


def test_invest_ratio_schema() -> None:
    js = InvestRatioResponse.model_json_schema()
    assert "example" in js


def test_expenditure_budget_schema() -> None:
    js = ExpenditureBudgetResponse.model_json_schema()
    assert "example" in js


def test_liability_schema() -> None:
    js = LiabilityResponse.model_json_schema()
    assert "example" in js


# ---- Sub-task 5-8: golden tests ----


def test_expenditure_ratio_golden(analytics_fixture_session: Session) -> None:
    expected = _golden()["expenditure_ratio"]
    actual = compute_expenditure_ratio(analytics_fixture_session, "202603")
    actual_dict = actual.model_dump()
    assert _normalise_items(actual_dict["outer"]) == _normalise_items(expected["outer"])
    assert _normalise_items(actual_dict["inner"]) == _normalise_items(expected["inner"])


def test_invest_ratio_golden(analytics_fixture_session: Session) -> None:
    expected = _golden()["invest_ratio"]
    actual = compute_invest_ratio(analytics_fixture_session, "202603").model_dump()
    assert _normalise_items(actual["items"]) == _normalise_items(expected["items"])


def test_expenditure_budget_golden(analytics_fixture_session: Session) -> None:
    expected = _golden()["expenditure_budget"]
    actual = compute_expenditure_budget(analytics_fixture_session, "202603").model_dump()
    assert _normalise_items(actual["rows"], key="action_main_type") == _normalise_items(
        expected["rows"], key="action_main_type"
    )


def test_liability_golden(analytics_fixture_session: Session) -> None:
    expected = _golden()["liability"]
    actual = compute_liability(analytics_fixture_session, "202603").model_dump()
    assert _normalise_items(actual["items"], key="credit_card_id") == _normalise_items(
        expected["items"], key="credit_card_id"
    )


# ---- Regression: capitalized action_main_type (real production casing) ----


def test_expenditure_ratio_excludes_capitalized_invest_transfer(
    capitalized_analytics_session: Session,
) -> None:
    """Capitalized Invest/Transfer rows must be excluded from the ratio.

    Regression: the exclusion used a lowercase ``in {"invest", "transfer"}``
    check that never matched real (capitalized) data, so invest/transfer leaked
    into both the outer (by main-type) and inner (by sub-type) groupings,
    inflating the ratio.
    """
    result = compute_expenditure_ratio(capitalized_analytics_session, "202603").model_dump()
    outer = {item["name"]: item["value"] for item in result["outer"]}
    inner = {item["name"]: item["value"] for item in result["inner"]}

    # Invest/Transfer main types are gone; their sub-types never appear.
    assert "Invest" not in outer
    assert "Transfer" not in outer
    assert "stock" not in inner
    assert "self" not in inner

    # The kept expense/income rows are unaffected.
    assert outer == {"Fixed": 2000.0, "Floating": 1000.0, "Income": 5000.0}
    assert inner == {"rent": 2000.0, "food": 1000.0, "salary": 5000.0}


def test_invest_ratio_includes_capitalized_invest(
    capitalized_analytics_session: Session,
) -> None:
    """compute_invest_ratio must match capitalized "Invest" rows.

    Regression: the ``!= "invest"`` guard skipped every row on capitalized data,
    so the invest ratio came back empty on real production data.
    """
    result = compute_invest_ratio(capitalized_analytics_session, "202603").model_dump()
    by_name = {item["name"]: item["value"] for item in result["items"]}
    assert by_name == {"stock": 800.0}


def test_expenditure_budget_aligns_mixed_casing(
    capitalized_analytics_session: Session,
) -> None:
    """Budget ``code_type`` and journal ``action_main_type`` align case-insensitively.

    Regression: the budget (``code_type="fixed"``) and the journal
    (``action_main_type="Fixed"``) differ only in casing; expected and actual
    must collapse into a single row instead of splitting into two.
    """
    result = compute_expenditure_budget(capitalized_analytics_session, "202603").model_dump()
    fixed_rows = [r for r in result["rows"] if r["action_main_type"].lower() == "fixed"]
    assert len(fixed_rows) == 1
    row = fixed_rows[0]
    assert row["expected"] == 1500.0
    assert row["actual"] == 2000.0
    assert row["diff"] == 500.0


# ---- Loan repayment: visible in the ratio pie (from Loan_Journal), not the budget ----


def test_expenditure_ratio_shows_loan_repayment_from_loan_journal(session: Session) -> None:
    """Loan repayment appears in the expenditure-ratio pie sourced ONLY from
    Loan_Journal (principal+interest) — the report-neutral LoanRepayment *Journal*
    row is still excluded, so the slice equals the Loan_Journal legs (no double-count).
    The budget remains unaffected (loan repayment is not a budgeted expense type).
    """
    from app.models.assets.loan import LoanJournal
    from app.models.monthly_report.journal import Journal

    session.add(
        Journal(
            vesting_month="202603", spend_date="20260310", spend_way="1",
            spend_way_type="account", spend_way_table="Account",
            action_main="FIX01", action_main_type="Fixed", action_main_table="Code_Data",
            action_sub=None, action_sub_type=None, action_sub_table=None,
            spending=-2000.0, invoice_number=None, note=None,
        )
    )
    # The report-neutral LoanRepayment Journal (signed -(principal+interest)); it
    # must NOT be counted — the pie's loan slice comes from Loan_Journal below.
    session.add(
        Journal(
            vesting_month="202603", spend_date="20260311", spend_way="1",
            spend_way_type="account", spend_way_table="Account",
            action_main="LoanRepayment", action_main_type="LoanRepayment",
            action_main_table="Loan", action_sub="LN-001", action_sub_type="Loan",
            action_sub_table="Loan", spending=-9200.0, invoice_number=None, note=None,
        )
    )
    session.add(LoanJournal(loan_id="LN-001", loan_excute_type="principal",
                            excute_price=8000.0, excute_date="20260311", memo=None))
    session.add(LoanJournal(loan_id="LN-001", loan_excute_type="interest",
                            excute_price=1200.0, excute_date="20260311", memo=None))
    session.commit()

    ratio = compute_expenditure_ratio(session, "202603").model_dump()
    outer = {i["name"]: i["value"] for i in ratio["outer"]}
    # 9200 == 8000 + 1200 (Loan_Journal), NOT 18400 — the -9200 Journal is ignored.
    assert outer == {"Fixed": 2000.0, "LoanRepayment": 9200.0}
    inner = {i["name"]: i["value"] for i in ratio["inner"]}
    assert inner["principal"] == 8000.0
    assert inner["interest"] == 1200.0

    budget = compute_expenditure_budget(session, "202603").model_dump()
    assert all(r["action_main_type"].lower() != "loanrepayment" for r in budget["rows"])


# ---- Sub-task 9-12: endpoint smoke tests ----


def test_get_expenditure_ratio_endpoint(client: TestClient) -> None:
    r = client.get("/monthly-report/journals/202603/expenditure-ratio")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == 1
    assert "outer" in body["data"] and "inner" in body["data"]


def test_get_invest_ratio_endpoint(client: TestClient) -> None:
    r = client.get("/monthly-report/journals/202603/invest-ratio")
    assert r.status_code == 200
    assert "items" in r.json()["data"]


def test_get_expenditure_budget_endpoint(client: TestClient) -> None:
    r = client.get("/monthly-report/journals/202603/expenditure-budget")
    assert r.status_code == 200
    assert "rows" in r.json()["data"]


def test_get_liability_endpoint(client: TestClient) -> None:
    r = client.get("/monthly-report/journals/202603/liability")
    assert r.status_code == 200
    assert "items" in r.json()["data"]


# ---- Sub-task 13: empty month returns valid empty structures ----


def test_analytics_empty_month_returns_empty_structures(client: TestClient) -> None:
    for sub in ("expenditure-ratio", "invest-ratio", "expenditure-budget", "liability"):
        r = client.get(f"/monthly-report/journals/209912/{sub}")
        assert r.status_code == 200, sub
        data = r.json()["data"]
        if sub == "expenditure-ratio":
            assert data == {"outer": [], "inner": []}
        elif sub == "expenditure-budget":
            assert data == {"rows": []}
        else:
            assert data == {"items": []}
