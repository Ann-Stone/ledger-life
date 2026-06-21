# Post-Frontend TODO

> Backend refactor (BE-001..BE-032) is complete on `main` as of 2026-04-26.
> The items below are intentionally deferred and **must be revisited after the
> frontend refactor lands**, because they either depend on frontend behavior
> being settled or risk breaking in-flight UI work if executed earlier.

---

## 1. BE-005 — Legacy data migration (Phase 1.5)

**Status**: Done — landed in commit `7236b69` (`BE-005: Migrate SQLite data
from account-book-API to new schema`). Row counts match legacy `ledger.db`
(Initial_Setting excluded).

---

## 2. Schema divergences from original refactor specs

These are places where the implemented model intentionally differs from the
ticket text. Each one needs a yes/no on "do we add a migration to align with
spec, or accept the divergence and document it?". Pick the answer **before**
BE-005 runs, since the import script encodes whichever choice is made.

| # | Area | Spec says | Implementation | Decision needed |
|---|------|-----------|----------------|-----------------|
| 1 | `Code_Data` hierarchy (BE-029) | `WHERE code_group IS NULL` for top-level | Uses `parent_id IS NULL`; `code_group` is an unrelated domain bucket | Confirm hierarchy stays on `parent_id`; rename or drop `code_group` if unused |
| 2 | `Loan.in_use` (BE-029) | filter `in_use == "Y"` | column does not exist; no filter applied | Add `in_use` column + migration, or accept "all loans returned" |
| 3 | `Insurance.in_use` (BE-029) | filter `in_use == "Y"` | column does not exist; uses `has_closed != "Y"` | Same: add column or accept current substitute |
| 4 | `Stock_Journal.vesting_nation` (BE-031) | distinct `(stock_code, vesting_nation)` for ticker fetch | column does not exist; `.TW` suffix derived from "all-digits" heuristic | Add column + backfill from legacy, or accept heuristic |
| 5 | `Credit_Card.carrier_no` (BE-031) | carrier match against `carrier_no` for invoice import | column dropped per README Decision Log; falls back to `card_no` last-4 match | Either restore `carrier_no` (legacy column was buggy) or drop the carrier→spend_way auto-fill entirely |
| 6 | `Journal.action_main_type` (BE-025) | literal `'Floating' / 'Fixed' / 'Income'` | implementation passes through whatever legacy stored (likely lowercase `expense` / `income`) | Decide canonical case; transform during BE-005 import |
| 7 | ~~`Target_Setting` PK (BE-027)~~ | ~~`id: int` PK + `setting_name` column~~ | actual table: `distinct_number: str` PK, `target_year/setting_value/is_done`, no `setting_name` | **Resolved 2026-05-02**: frontend (FE-002) aligned with the shipped shape; no migration needed. Row kept here for audit only. |
| 8 | Several Phase 4 asset PKs | `int` autoincrement | several use string business keys instead | Listed previously as "Phase 4 int-PK divergence"; bundle with the above when deciding |

Suggested approach: open one follow-up ticket (BE-B02 perhaps) that
enumerates all 8 rows, lets the frontend agent flag which fields it actually
reads, and then we either ship a single Alembic migration or a single
"transform map" used by BE-005 — but not both piecemeal.

---

## 3. Items contingent on frontend usage — checklist

These are not bugs, just decisions waiting on the frontend to declare its
needs. **Update each row as the relevant frontend page is implemented**:
fill in `Verified at` (the view/component path or PR link), set `Decision`
to `keep` or `drop`, and record the frontend commit. This file is the
single source of truth; do not scatter the same notes inside frontend code.

> **Hard gate**: every frontend refactor session's phase-exit checklist
> MUST include a step "rows in POST_FRONTEND_TODO.md §3 touched by this
> phase have been updated". Do not declare a frontend phase done until
> the table below reflects what was actually consumed.

| Field | Origin / current note | Verified at | Decision | Frontend commit |
|-------|-----------------------|-------------|----------|-----------------|
| `Account.discount` | kept per Decision Log; "confirmed in use" | view/src/views/setting/MenuSettingView.vue | keep | c95016b |
| `Account.owner` | kept per Decision Log; "confirmed in use" | view/src/views/setting/MenuSettingView.vue | keep | c95016b |
| `Account.account_index` | drives dropdown order | view/src/views/setting/MenuSettingView.vue | keep | c95016b |
| `Credit_Card.credit_card_index` | drives dropdown order | view/src/views/setting/MenuSettingView.vue | keep | da0fe5b |
| `Other_Asset.asset_index` | drives dropdown order; per api/docs/api-reference/assets/other-assets.md the field orders the categories table and the per-tab parent selectors (stocks/estates/insurances) | view/src/views/other-assets/OtherAssetsView.vue | keep | 191b7ae |
| `Journal.invoice_number` | populated only by invoice CSV import; if unused, the entire BE-031 invoice path is dead weight | view/src/views/monthly-report/CashFlowView.vue | keep | 2f87798 |
| `Loan.grace_expire_date` | kept per Decision Log; field present in api/docs/api-reference/assets/loans.md, rendered as optional table column + form date picker | view/src/views/other-assets/OtherAssetsView.vue | keep | 9214fdf |
| `Stock_Journal.expected_spend` | planned-investment amount; verified field exists only on Stock parent (assets/stocks.md), not on Stock_Journal (assets/stocks-details.md) | view/src/views/other-assets/OtherAssetsView.vue | drop | e7b372e |

When `Decision = drop` is set on every row that ends up unused, open one
cleanup ticket (BE-B03 perhaps) that bundles the column drops + Alembic
migration + any service / response-model trim, rather than dropping rows
one-by-one.

---

## 4. Backlog tickets

| ID | Title | Trigger to revisit |
|----|-------|--------------------|
| BE-B01 | User management CRUD endpoints | Frontend refactor confirms whether single-user assumption holds; legacy `userRouter.py` was never registered |

---

## 5. Operational follow-ups (not blocked on frontend, but easy to forget)

- **`api/config/invoice_skip.json` and `merchant_mapping.json`**: shipped as
  empty defaults. Real user values from the legacy hardcoded map
  (`account-book-API/globalRouter.py:261-264`) need to be migrated:
  `台灣之星` → `92`, `台灣大哥大` → `100`, `台灣中油` → `4/32`. Decide whether
  to commit these as defaults or keep them out of source control.
- **`api/logs/`**: gitignored. Confirm production deploys mount a writable
  path or redirect logs to stdout.
- **`template.html`** at repo root: untracked across many sessions. Either
  commit, move into `view/`, or delete.
- **CI workflow `.github/workflows/ci.yml`**: only runs on `api/**` changes.
  Verify GitHub Actions has `uv` cache enabled and that the runner image
  ships Python 3.13 (current spec assumes `actions/setup-python@v5` with
  `python-version: '3.13'`).

---

## 6. Re-run on every visit

When this file is opened:

1. Cross-check section 1: is BE-005 still deferred? If frontend is
   ready, the unblocking trigger is met.
2. Cross-check section 2: walk each row with the frontend AI's API
   contract output (`api/docs/api-reference.md` is the spec; what fields
   does the frontend actually read?). Mark rows as "drop" or "migrate"
   accordingly.
3. Section 5 items can be tackled independently any time.

Once everything in sections 1–4 is resolved, this file can be deleted.
