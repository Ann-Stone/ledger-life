# Reports — Budget Variance

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /reports/budget-variance/{year}

**Get annual budget vs actual variance**

Per expense category: annual expected (Budget sum of expected01..12, or annual_amount for annual-event categories) vs actual FX-converted spend for the year, with diff, usage rate, and a run-rate projection. Income, invest and transfer categories are excluded.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| year | path | string | yes | Budget year YYYY |

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
| year | string | yes | Budget year YYYY |
| rows | array<BudgetVarianceRow> | yes | Per-category rows, ordered by actual descending |
| summary | BudgetVarianceSummary | yes | Totals and run-rate projection |

Example:

```json
{
  "status": 1,
  "data": {
    "rows": [
      {
        "actual": 372000.0,
        "code": "F01",
        "diff": 12000.0,
        "expected": 360000.0,
        "name": "居住",
        "type": "Fixed",
        "usage_rate": 1.0333
      }
    ],
    "summary": {
      "elapsed_months": 6,
      "projected_total": 720000.0,
      "total_actual": 360000.0,
      "total_diff": -420000.0,
      "total_expected": 780000.0,
      "usage_rate": 0.4615
    },
    "year": "2026"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
