# Dashboard — Retirement

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /dashboard/retirement

**Retirement readiness**

Point-in-time readiness on the consumption basis: target_portfolio = annual_expense_base / withdrawal_rate (loan excluded from the base), readiness = net_worth / target. Also returns debt-service-to-income and per-loan payoff projection for the during-loan cash-flow check.

#### Response (200)

Envelope:

| name | type | required | description |
| --- | --- | --- | --- |
| status | integer | no | 1 = success, 0 = fail |
| data |  | no | Response payload. Shape depends on the endpoint. |
| msg | string | no | Human-readable status message |

data:

| name | type | required | description |
| --- | --- | --- | --- |
| net_worth | number | yes | Net worth (TWD) used for the readiness target; from the balance sheet (already nets the loan), minus self-occupied housing when exclude_self_occupied_estate is on |
| exclude_self_occupied_estate | boolean | yes | Whether self-occupied (estate_status 'live') housing was excluded from net_worth |
| self_occupied_estate_value | number | yes | Self-occupied housing market value excluded from net_worth (TWD); 0 when the toggle is off or no estate is marked 'live' |
| annual_expense_base | number | yes | Annual retirement expense base (TWD), consumption-basis (loan excluded) |
| expense_base_source | string (enum: 'computed', 'override') | yes | 'computed' = trailing-12-month consumption; 'override' = manual setting |
| withdrawal_rate | number | yes | Safe withdrawal rate used |
| target_portfolio | number | yes | annual_expense_base / withdrawal_rate (the FIRE number), TWD |
| readiness_pct | number | yes | net_worth / target_portfolio (≥1.0 means target reached) |
| gap | number | yes | target_portfolio − net_worth (TWD; ≤0 means surplus) |
| monthly_income | number | yes | Trailing-12-month average monthly income (TWD) |
| monthly_loan_payment | number | yes | Trailing-12-month average monthly loan payment (principal+interest), TWD |
| debt_service_ratio | number | yes | monthly_loan_payment / monthly_income (cash-flow health; 0 when no income) |
| loans | array<LoanPayoff> | no | Per-loan remaining balance + projected payoff |

Example:

```json
{
  "status": 1,
  "data": {
    "annual_expense_base": 600000.0,
    "debt_service_ratio": 0.3111,
    "exclude_self_occupied_estate": true,
    "expense_base_source": "computed",
    "gap": 7000000.0,
    "loans": [
      {
        "loan_id": "LN-001",
        "loan_name": "房貸",
        "monthly_payment": 28000.0,
        "payoff_month": "203406",
        "remaining_balance": 3200000.0,
        "years_left": 8.5
      }
    ],
    "monthly_income": 90000.0,
    "monthly_loan_payment": 28000.0,
    "net_worth": 8000000.0,
    "readiness_pct": 0.5333,
    "self_occupied_estate_value": 0.0,
    "target_portfolio": 15000000.0,
    "withdrawal_rate": 0.04
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
