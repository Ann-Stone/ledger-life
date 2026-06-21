# Reports — Cash Flow

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /reports/cash-flow/{type}

**Get personal cash-flow statement**

Cash flow over the monthly (trailing 12 months) or yearly (trailing 10 years) window, split into three activities: operating (生活: income − living − loan interest), investing (投資), financing (債務: loan principal / new borrowing). FX-converted; self-transfers excluded.

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
| points | array<CashFlowPoint> | yes | Per-period cash-flow series, oldest first |
| summary | CashFlowSummary | yes | Window-level activity breakdown + overall net change |

Example:

```json
{
  "status": 1,
  "data": {
    "points": [
      {
        "financing": -7000.0,
        "investing": -15000.0,
        "net_change": 15000.0,
        "operating": 37000.0,
        "period": "202403"
      }
    ],
    "summary": {
      "activities": [
        {
          "items": [
            {
              "amount": 960000.0,
              "label": "收入"
            },
            {
              "amount": -516000.0,
              "label": "生活支出"
            }
          ],
          "key": "operating",
          "label": "生活",
          "net": 444000.0
        }
      ],
      "net_change": 123000.0
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
