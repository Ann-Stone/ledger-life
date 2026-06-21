# Networth API Reference

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

- OpenAPI version: `3.1.0`
- API version: `0.1.0`

## How to read this directory

Each sub-router has its own self-contained markdown file under `api-reference/<domain>/<sub-router>.md`, with the matching JSON slice at `openapi/<domain>/<sub-router>.json` for drill-down. Every file is kept under 500 lines so the frontend granularization AI can pull just the slice it needs without ingesting the whole API.

Frontend tickets that touch a single resource (`/settings/accounts`, `/assets/stocks`, …) read **only** the matching sub-router file. Tickets that span a whole domain (e.g. `FE-003 — src/api/setting.ts`) read every file under that domain folder.

## Index

### Settings

| Sub-router | Markdown | OpenAPI slice | Endpoints |
| --- | --- | --- | --- |
| `accounts` | [api-reference/settings/accounts.md](api-reference/settings/accounts.md) | [openapi/settings/accounts.json](openapi/settings/accounts.json) | 5 |
| `alarms` | [api-reference/settings/alarms.md](api-reference/settings/alarms.md) | [openapi/settings/alarms.json](openapi/settings/alarms.json) | 5 |
| `budgets` | [api-reference/settings/budgets.md](api-reference/settings/budgets.md) | [openapi/settings/budgets.json](openapi/settings/budgets.json) | 5 |
| `codes` | [api-reference/settings/codes.md](api-reference/settings/codes.md) | [openapi/settings/codes.json](openapi/settings/codes.json) | 4 |
| `codes-tree` | [api-reference/settings/codes-tree.md](api-reference/settings/codes-tree.md) | [openapi/settings/codes-tree.json](openapi/settings/codes-tree.json) | 2 |
| `credit-cards` | [api-reference/settings/credit-cards.md](api-reference/settings/credit-cards.md) | [openapi/settings/credit-cards.json](openapi/settings/credit-cards.json) | 4 |
| `stock-categories` | [api-reference/settings/stock-categories.md](api-reference/settings/stock-categories.md) | [openapi/settings/stock-categories.json](openapi/settings/stock-categories.json) | 4 |
| `sub-codes` | [api-reference/settings/sub-codes.md](api-reference/settings/sub-codes.md) | [openapi/settings/sub-codes.json](openapi/settings/sub-codes.json) | 3 |

### Monthly Report

| Sub-router | Markdown | OpenAPI slice | Endpoints |
| --- | --- | --- | --- |
| `balance` | [api-reference/monthly-report/balance.md](api-reference/monthly-report/balance.md) | [openapi/monthly-report/balance.json](openapi/monthly-report/balance.json) | 1 |
| `estate-values` | [api-reference/monthly-report/estate-values.md](api-reference/monthly-report/estate-values.md) | [openapi/monthly-report/estate-values.json](openapi/monthly-report/estate-values.json) | 4 |
| `insurance-values` | [api-reference/monthly-report/insurance-values.md](api-reference/monthly-report/insurance-values.md) | [openapi/monthly-report/insurance-values.json](openapi/monthly-report/insurance-values.json) | 2 |
| `journals` | [api-reference/monthly-report/journals.md](api-reference/monthly-report/journals.md) | [openapi/monthly-report/journals.json](openapi/monthly-report/journals.json) | 5 |
| `journals-analytics` | [api-reference/monthly-report/journals-analytics.md](api-reference/monthly-report/journals-analytics.md) | [openapi/monthly-report/journals-analytics.json](openapi/monthly-report/journals-analytics.json) | 4 |
| `journals-transactions` | [api-reference/monthly-report/journals-transactions.md](api-reference/monthly-report/journals-transactions.md) | [openapi/monthly-report/journals-transactions.json](openapi/monthly-report/journals-transactions.json) | 8 |
| `stock-prices` | [api-reference/monthly-report/stock-prices.md](api-reference/monthly-report/stock-prices.md) | [openapi/monthly-report/stock-prices.json](openapi/monthly-report/stock-prices.json) | 2 |

### Assets

| Sub-router | Markdown | OpenAPI slice | Endpoints |
| --- | --- | --- | --- |
| `estates` | [api-reference/assets/estates.md](api-reference/assets/estates.md) | [openapi/assets/estates.json](openapi/assets/estates.json) | 4 |
| `estates-details` | [api-reference/assets/estates-details.md](api-reference/assets/estates-details.md) | [openapi/assets/estates-details.json](openapi/assets/estates-details.json) | 4 |
| `insurances` | [api-reference/assets/insurances.md](api-reference/assets/insurances.md) | [openapi/assets/insurances.json](openapi/assets/insurances.json) | 4 |
| `insurances-details` | [api-reference/assets/insurances-details.md](api-reference/assets/insurances-details.md) | [openapi/assets/insurances-details.json](openapi/assets/insurances-details.json) | 4 |
| `loans` | [api-reference/assets/loans.md](api-reference/assets/loans.md) | [openapi/assets/loans.json](openapi/assets/loans.json) | 5 |
| `loans-details` | [api-reference/assets/loans-details.md](api-reference/assets/loans-details.md) | [openapi/assets/loans-details.json](openapi/assets/loans-details.json) | 4 |
| `loans-selection` | [api-reference/assets/loans-selection.md](api-reference/assets/loans-selection.md) | [openapi/assets/loans-selection.json](openapi/assets/loans-selection.json) | 1 |
| `other-assets` | [api-reference/assets/other-assets.md](api-reference/assets/other-assets.md) | [openapi/assets/other-assets.json](openapi/assets/other-assets.json) | 5 |
| `stocks` | [api-reference/assets/stocks.md](api-reference/assets/stocks.md) | [openapi/assets/stocks.json](openapi/assets/stocks.json) | 5 |
| `stocks-details` | [api-reference/assets/stocks-details.md](api-reference/assets/stocks-details.md) | [openapi/assets/stocks-details.json](openapi/assets/stocks-details.json) | 4 |

### Reports

| Sub-router | Markdown | OpenAPI slice | Endpoints |
| --- | --- | --- | --- |
| `assets` | [api-reference/reports/assets.md](api-reference/reports/assets.md) | [openapi/reports/assets.json](openapi/reports/assets.json) | 1 |
| `balance` | [api-reference/reports/balance.md](api-reference/reports/balance.md) | [openapi/reports/balance.json](openapi/reports/balance.json) | 1 |
| `budget-variance` | [api-reference/reports/budget-variance.md](api-reference/reports/budget-variance.md) | [openapi/reports/budget-variance.json](openapi/reports/budget-variance.json) | 1 |
| `cash-flow` | [api-reference/reports/cash-flow.md](api-reference/reports/cash-flow.md) | [openapi/reports/cash-flow.json](openapi/reports/cash-flow.json) | 1 |
| `expenditure` | [api-reference/reports/expenditure.md](api-reference/reports/expenditure.md) | [openapi/reports/expenditure.json](openapi/reports/expenditure.json) | 1 |
| `expenditure-composition` | [api-reference/reports/expenditure-composition.md](api-reference/reports/expenditure-composition.md) | [openapi/reports/expenditure-composition.json](openapi/reports/expenditure-composition.json) | 1 |
| `expense-insights` | [api-reference/reports/expense-insights.md](api-reference/reports/expense-insights.md) | [openapi/reports/expense-insights.json](openapi/reports/expense-insights.json) | 1 |
| `income-expense` | [api-reference/reports/income-expense.md](api-reference/reports/income-expense.md) | [openapi/reports/income-expense.json](openapi/reports/income-expense.json) | 1 |
| `income-statement` | [api-reference/reports/income-statement.md](api-reference/reports/income-statement.md) | [openapi/reports/income-statement.json](openapi/reports/income-statement.json) | 1 |
| `stock-allocation` | [api-reference/reports/stock-allocation.md](api-reference/reports/stock-allocation.md) | [openapi/reports/stock-allocation.json](openapi/reports/stock-allocation.json) | 1 |

### Dashboard

| Sub-router | Markdown | OpenAPI slice | Endpoints |
| --- | --- | --- | --- |
| `alarms` | [api-reference/dashboard/alarms.md](api-reference/dashboard/alarms.md) | [openapi/dashboard/alarms.json](openapi/dashboard/alarms.json) | 1 |
| `budget` | [api-reference/dashboard/budget.md](api-reference/dashboard/budget.md) | [openapi/dashboard/budget.json](openapi/dashboard/budget.json) | 1 |
| `gifts` | [api-reference/dashboard/gifts.md](api-reference/dashboard/gifts.md) | [openapi/dashboard/gifts.json](openapi/dashboard/gifts.json) | 1 |
| `summary` | [api-reference/dashboard/summary.md](api-reference/dashboard/summary.md) | [openapi/dashboard/summary.json](openapi/dashboard/summary.json) | 1 |
| `targets` | [api-reference/dashboard/targets.md](api-reference/dashboard/targets.md) | [openapi/dashboard/targets.json](openapi/dashboard/targets.json) | 4 |

### Utilities

| Sub-router | Markdown | OpenAPI slice | Endpoints |
| --- | --- | --- | --- |
| `import` | [api-reference/utilities/import.md](api-reference/utilities/import.md) | [openapi/utilities/import.json](openapi/utilities/import.json) | 3 |
| `selections` | [api-reference/utilities/selections.md](api-reference/utilities/selections.md) | [openapi/utilities/selections.json](openapi/utilities/selections.json) | 10 |

### Health

| Sub-router | Markdown | OpenAPI slice | Endpoints |
| --- | --- | --- | --- |
| `(root)` | [api-reference/health.md](api-reference/health.md) | [openapi/health.json](openapi/health.json) | 1 |

## Monthly Report — Polymorphic references

Journal rows carry two polymorphic foreign keys. Frontend forms must keep the
discriminator and the table consistent or the row will fail validation on the
server. The full matrix is:

| field group | type value | table value | id value points to | source endpoint |
| --- | --- | --- | --- | --- |
| `spend_way_*` | `account` | `Account` | `Account.id` (PK) | `GET /utilities/selections/accounts` |
| `spend_way_*` | `credit_card` | `Credit_Card` | `CreditCard.credit_card_id` | `GET /utilities/selections/credit-cards` |
| `action_main_*` | `Fixed` / `Floating` / `Income` / `Invest` / `Transfer` (user-configurable, mirrors `Code_Data.code_type`) | `Code_Data` | `Code_Data.code_id` (where `parent_id IS NULL`) | `GET /utilities/selections/codes` |
| `action_sub_*` | mirror of the sub-code's `Code_Data.code_type`, or `null` | `Code_Data` or `null` | `Code_Data.code_id` whose `parent_id == action_main`, or `null` | `GET /utilities/selections/codes/{action_main}` |

Hard rules the API enforces:

- `spend_way_table` must match the `spend_way_type` mapping above; mismatched values cause a 422.
- All three `action_sub_*` fields are populated together, or all three are `null`. Partial population is rejected.
- `action_main_table` is always `"Code_Data"` for journal entries created by the UI; legacy importers may emit other table names but new writes must use `Code_Data`.

## Shared OpenAPI components

The `openapi/_shared.json` file contains schemas referenced by every sub-router (response envelope, error envelope, framework validation schemas). Each sub-router JSON inlines the schemas it uses, so it is self-contained — `_shared.json` is provided as a convenience for tools that want the canonical envelope definition without resolving duplicates.
