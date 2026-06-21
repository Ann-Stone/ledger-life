# Dashboard — Budget

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /dashboard/budget

**Get budget vs actual**

Returns per-category budget-vs-actual for a month (YYYYMM) or year (YYYY).

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| type | query |  | yes | Aggregation granularity |
| period | query | string | yes | YYYYMM for monthly, YYYY for yearly |

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
| type | BudgetType | yes | Aggregation granularity |
| period | string | yes | YYYYMM for monthly, YYYY for yearly |
| lines | array<BudgetLine> | yes | Per-category rows (ordinary monthly categories) |
| total_planned | number | yes | Sum of planned across lines |
| total_actual | number | yes | Sum of actual across lines |
| event_lines | array<BudgetLine> | no | Annual-event categories: planned=annual envelope, actual=year-to-date. Excluded from lines/totals. |
| event_total_planned | number | no | Sum of planned across event_lines |
| event_total_actual | number | no | Sum of actual across event_lines |

Example:

```json
{
  "status": 1,
  "data": {
    "lines": [
      {
        "actual": 8700.0,
        "category": "Food",
        "planned": 10000.0,
        "usage_pct": 87.0
      }
    ],
    "period": "202403",
    "total_actual": 8700.0,
    "total_planned": 10000.0,
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
