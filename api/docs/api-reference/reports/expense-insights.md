# Reports — Expense Insights

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /reports/expense-insights/{year}

**Get year-over-year change + largest transactions**

Per expense category: this year vs prior-year actual with YoY rate (ordered by absolute change), plus the year's largest individual expense transactions. FX-converted; only Fixed/Floating rows count.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| year | path | string | yes | Calendar year YYYY |

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
| year | string | yes | Calendar year YYYY |
| yoy | array<YoYRow> | yes | Per-category YoY, ordered by |delta| descending |
| largest | array<LargeTxn> | yes | Largest expense transactions, amount descending |

Example:

```json
{
  "status": 1,
  "data": {
    "largest": [
      {
        "amount": 85000.0,
        "category": "旅遊",
        "date": "20260815",
        "note": "日本機票",
        "pay_way": "Chase Sapphire"
      }
    ],
    "year": "2026",
    "yoy": [
      {
        "code": "E01",
        "current": 192000.0,
        "delta": 24000.0,
        "name": "餐飲",
        "previous": 168000.0,
        "type": "Floating",
        "yoy_rate": 0.1429
      }
    ]
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
