# Reports — Income Expense

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /reports/income-expense/{type}

**Get income vs expense + savings rate**

Returns monthly (12 points) or yearly (10 points) income / fixed / floating / net per period, plus an annual summary (total income, total expense, net savings, savings rate). Amounts are FX-converted to the base currency; invest and transfer rows are excluded.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| type | path | string | yes |  |
| vesting_month | query | string | yes | Anchor month YYYYMM |

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
| type | string (enum: 'monthly', 'yearly') | yes | Aggregation granularity |
| points | array<IncomeExpensePoint> | yes | Time series, oldest first |
| summary | IncomeExpenseSummary | yes | Totals and savings rate across the window |

Example:

```json
{
  "status": 1,
  "data": {
    "points": [
      {
        "expense": 43000.0,
        "fixed": 25000.0,
        "floating": 18000.0,
        "income": 80000.0,
        "net": 37000.0,
        "period": "202403"
      }
    ],
    "summary": {
      "net": 444000.0,
      "savings_rate": 0.4625,
      "total_expense": 516000.0,
      "total_income": 960000.0
    },
    "type": "monthly"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
