# Reports — Stock Allocation

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /reports/stock-allocation

**Get stock allocation by category**

Returns the share (% + absolute) of stock value per allocation category (growth / bond / cash-equivalent / …), FX-converted to base currency. Holdings with no category fall into the '未分類' (unclassified) bucket.

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
| total | number | yes | Total stock value in base currency |
| items | array<StockAllocationShare> | yes | Per-category share, sums to 100% within rounding |

Example:

```json
{
  "status": 1,
  "data": {
    "items": [
      {
        "amount": 200000.0,
        "category_id": "SC-001",
        "category_name": "成長型",
        "share": 55.0
      },
      {
        "amount": 100000.0,
        "category_id": "SC-002",
        "category_name": "債券",
        "share": 27.5
      },
      {
        "amount": 63636.36,
        "category_name": "未分類",
        "share": 17.5
      }
    ],
    "total": 363636.36
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
