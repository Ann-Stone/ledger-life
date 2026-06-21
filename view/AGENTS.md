# Balance Sheet View — QA Strategy & Checklists

> Architecture / conventions / common pitfalls live in **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)**. This file is QA-only.

---

## Project-Specific Architectural Signals

Treat these as architectural (worth a design pass before changing):
- Breaking changes to `src/types/models.ts`.
- Adding or changing a Pinia store's state shape under `src/stores/`.
- New routes or changes to `src/router/index.ts`.
- New shared composable or new component under `src/components/`.

---

## Test Strategy

- **Unit / store tests** (Vitest, colocated `*.spec.ts` or under `src/__tests__/`): utility functions in `src/utils/`, Pinia store actions and state transitions, calculation logic.
- **Component tests** (Vue Test Utils + Vitest): props render correctly, emits fire with expected payloads, money values show the right colour class (positive/negative).
- **E2E** (Playwright — Phase 2): navigation, form submit, MSW-mocked API responses.

---

## Validation Checklist by Feature

Business rules to verify before declaring a feature done.

### Dashboard
- [ ] Asset trend chart renders with correct data points.
- [ ] Period toggle (month/year) changes chart data.
- [ ] Date picker disables future dates.
- [ ] Alarm list shows unpaid reminders only.
- [ ] Summary cards show correct totals (assets, liabilities, net assets).

### Monthly Cash Flow
- [ ] `Gain/Loss = Income − Expense`.
- [ ] Budget-vs-actual shows correct diff values.
- [ ] Negative diff (over budget) shown in red.
- [ ] Liability changes table shows begin/end balance correctly.
- [ ] Stock price update dialog validates numeric input.

### Balance Sheet
- [ ] `Net Assets = Total Assets − Total Liabilities`.
- [ ] Every asset category subtotal sums to Total Assets.
- [ ] Every liability category subtotal sums to Total Liabilities.
- [ ] Positive net assets in green, negative in red.

### Other Assets — Stock
- [ ] Stock list shows all holdings.
- [ ] `ROI = (Current − Buy) / Buy × 100%`.
- [ ] Add/Edit form validates required fields (code, name, buyPrice, quantity).
- [ ] Delete shows confirmation dialog.

### Other Assets — Estate / Insurance / Liability
- [ ] CRUD works for each tab.
- [ ] Form validation prevents empty required fields.
- [ ] List refreshes automatically after add/edit.

### Budget Settings
- [ ] Items grouped by floating / fixed type.
- [ ] Year selector only allows valid range.
- [ ] Edit mode enables inline editing.
- [ ] Copy-previous-year creates new records.

### Remind Settings
- [ ] Reminders show month and amount.
- [ ] `isPaid` toggle updates correctly.

### Menu Settings
- [ ] Add/edit/delete works across all 5 tabs.
- [ ] Cash flow codes support sub-codes.
- [ ] Sub-code operations don't affect parent.

---

## Edge Cases to Always Test

| Scenario | Expected |
|----------|----------|
| Empty data (no transactions) | Empty state, no error. |
| Zero values in tables | Display `0`, not blank. |
| Very large numbers (> 1,000,000,000) | Formatted with commas, no overflow. |
| Negative balance / ROI | Red, with minus sign. |
| Future date selection | Disabled in date pickers. |
| Network error (mock API down) | `ElMessage` error shown, no crash. |
| Duplicate code / account name | Backend error displayed in the form. |

---

## QA Pass Criteria

1. Feature checklist + edge cases verified.
2. `pnpm type-check` zero errors.
3. No errors in browser DevTools console.
4. Tested at 1280px (desktop) and 375px (mobile) viewports.
5. All open issues resolved or explicitly deferred.
