# Reports — Expenditure

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /reports/expenditure/{type}

**Get expenditure trend**

Returns monthly (12 points) or yearly (10 points) expenditure aggregated from Journal rows whose action_main_type is Floating or Fixed.

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
| points | array<ExpenditurePoint> | yes | Time series, oldest first |

Example:

```json
{
  "status": 1,
  "data": {
    "points": [
      {
        "amount": 45200.0,
        "period": "202403"
      },
      {
        "amount": 38500.0,
        "period": "202404"
      }
    ],
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
