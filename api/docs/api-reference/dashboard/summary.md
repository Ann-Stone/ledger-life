# Dashboard — Summary

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /dashboard/summary

**Get dashboard summary**

Returns spending / freedom_ratio / asset_debt_trend time series for the requested period (YYYYMM-YYYYMM).

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| type | query |  | yes | Summary variant |
| period | query | string | yes | YYYYMM-YYYYMM |

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
| type | SummaryType | yes | Summary variant |
| points | array<SummaryPoint> | yes | Time series, oldest first |

Example:

```json
{
  "status": 1,
  "data": {
    "points": [
      {
        "breakdown": {
          "accounts": 480000.0,
          "cards": -3000.0,
          "estates": 470000.0,
          "insurances": 23000.0,
          "loans": -230000.0,
          "stocks": 310000.0
        },
        "period": "202301",
        "value": 1050000.0
      },
      {
        "breakdown": {
          "accounts": 500000.0,
          "cards": -3000.0,
          "estates": 480000.0,
          "insurances": 24000.0,
          "loans": -240000.0,
          "stocks": 320000.0
        },
        "period": "202302",
        "value": 1081000.0
      }
    ],
    "type": "asset_debt_trend"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
