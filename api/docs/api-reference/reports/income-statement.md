# Reports — Income Statement

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /reports/income-statement/{type}

**Get comprehensive income statement (本業/投資/綜合損益)**

Returns monthly (12 points) or yearly (10 points) profit-and-loss per period in three sections: 本業損益 (active income − living expenses), 投資損益 (dividends + realized capital gains + unrealized market-value change), and 綜合損益 (their sum), plus a window summary. Amounts are FX-converted to the base currency. Realized gains come from booked 資本利得 journals; unrealized covers stock holdings only.

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
| points | array<IncomeStatementPoint> | yes | Time series, oldest first |
| summary | IncomeStatementSummary | yes | Section totals across the window |

Example:

```json
{
  "status": 1,
  "data": {
    "points": [
      {
        "active_income": 80000.0,
        "comprehensive_net": 57000.0,
        "dividend": 3000.0,
        "fixed": 25000.0,
        "floating": 18000.0,
        "investment_net": 20000.0,
        "loan_interest": 0.0,
        "operating_net": 37000.0,
        "period": "202403",
        "realized": 5000.0,
        "unrealized": 12000.0
      }
    ],
    "summary": {
      "active_income": 960000.0,
      "comprehensive_net": 684000.0,
      "dividend": 36000.0,
      "fixed": 300000.0,
      "floating": 216000.0,
      "investment_net": 240000.0,
      "loan_interest": 0.0,
      "operating_net": 444000.0,
      "realized": 60000.0,
      "unrealized": 144000.0
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
