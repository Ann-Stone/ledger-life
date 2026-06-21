# Networth API — QA Strategy & Checklists

> Architecture / conventions / API documentation discipline / common pitfalls live in **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)**. This file is QA-only.

---

## Test Strategy

- **Unit tests** (`tests/`, organised by domain): service calculation logic, model schema field constraints, date parsing / format conversion.
- **API tests** (httpx `TestClient`): CRUD correctness (status codes, response shape), query filter combinations, error responses (404, 422).
- **Fixtures**: shared in-memory SQLite engine via `conftest.py`; per-domain pre-populated test data.

Calculation-heavy services (BE-017, BE-019, BE-025, BE-026) additionally require a golden test against a fixture DB snapshot.

---

## Validation Checklist by Domain

Business rules to verify before declaring a feature done. The `Initial_Setting` table is intentionally dropped (orphan in legacy code) — there is no Initial-Setting endpoint.

### Settings
- [ ] Account CRUD: create, read with filters (name / type / `in_use`), update, delete.
- [ ] Code CRUD: auto-create Budget when `code_type` is Fixed / Floating.
- [ ] Sub-code CRUD: correctly linked to parent via `parent_id`.
- [ ] Budget: year-range query, batch update, copy-from-previous calculation.
- [ ] Credit Card CRUD: filter by `in_use`.
- [ ] Alarm CRUD: date format YYYYMMDD, by-date query.

### Monthly Report
- [ ] Journal CRUD: date conversion (legacy → YYYYMMDD).
- [ ] Journal GET: `gainLoss` calculation (income − expense).
- [ ] Expenditure ratio: outer / inner layer grouping correct.
- [ ] Expenditure vs budget: expected vs actual per category.
- [ ] Liability: credit-card grouped totals.
- [ ] Stock price: GET by month, POST new records.
- [ ] Settlement: all six history tables populated; idempotent (re-run safe).
- [ ] Settlement: full rollback on any step failure.

### Assets
- [ ] Stock holdings + transaction details (buy / sell / dividend).
- [ ] Insurance policies + payment / claim details.
- [ ] Real estate + expense / tax records.
- [ ] Loans + repayment details (principal / interest / fee).
- [ ] `Loan.repayed` auto-recalculated on detail change.
- [ ] Other Asset CRUD, distinct `asset_type` list.

### Reports
- [ ] Balance sheet: `net_worth = total_assets − total_liabilities`.
- [ ] Expenditure monthly: 12-month lookback aggregation.
- [ ] Expenditure yearly: 10-year lookback aggregation.
- [ ] Asset breakdown: FX rate conversion applied.

### Dashboard
- [ ] Summary spending: monthly totals for period.
- [ ] Freedom ratio: `(income − fixed) / income`.
- [ ] Asset / debt trend: combined LoanBalance + CreditCardBalance.
- [ ] Budget: monthly and yearly comparison.
- [ ] Targets CRUD: `is_done` toggle.
- [ ] Alarms: future 6 months only, sorted by date.
- [ ] Gifts: grouped by recipient, yearly totals.

### Utilities
- [ ] Selection groups: correct `label` / `options` shape for `el-select`.
- [ ] Health check: returns alive status.
- [ ] Stock import: background task, yfinance retry, upsert.
- [ ] FX import: background task, upsert by `date + code`.
- [ ] Invoice CSV: pipe-delimited, M/D parsing, dedup by invoice number.
- [ ] Invoice CSV: file not found → error log, no crash.

---

## Edge Cases to Always Test

| Scenario | Expected |
|----------|----------|
| Empty table (no data) | Return empty list `[]`, not error. |
| Zero amount in journal | Store and display `0.0`. |
| Very large numbers (> 1B) | No overflow, correct aggregation. |
| Non-existent ID on GET/PUT/DELETE | HTTP 404 with `ApiError`. |
| Duplicate PK insert | HTTP 409 or appropriate error. |
| Settlement re-run (same month) | Clears old snapshots, recalculates — idempotent. |
| Settlement partial failure | Full rollback, no partial data. |
| CSV file missing | Background task logs error, no crash. |
| CSV with wrong delimiter | Graceful error handling. |
| Future date in alarm query | Included if within the 6-month window. |
| Budget copy with no previous-year data | Meaningful error returned. |

---

## QA Pass Criteria

1. Domain checklist + edge cases verified.
2. `uv run pytest` passes; coverage ≥ 70%.
3. No unhandled exceptions in server logs.
4. All endpoints return correct `ApiResponse` / `ApiError` envelope.
5. Background tasks complete without crash.
