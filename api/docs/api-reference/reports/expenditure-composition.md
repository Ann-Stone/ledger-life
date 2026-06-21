# Reports — Expenditure Composition

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /reports/expenditure-composition/{type}

**Get expenditure composition tree**

Category → subcategory tree of expense magnitude over the monthly (trailing 12 months) or yearly (trailing 10 years) window, each node carrying its share of the grand total. FX-converted to base currency; only Fixed and Floating rows are counted.

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
| total | number | yes | Grand total expense in base currency |
| fixed_total | number | yes | Sum of Fixed-type categories |
| floating_total | number | yes | Sum of Floating-type categories |
| categories | array<ExpenditureCategoryNode> | yes | Category nodes, ordered by amount descending |

Example:

```json
{
  "status": 1,
  "data": {
    "categories": [
      {
        "amount": 42000.0,
        "children": [
          {
            "amount": 18000.0,
            "code": "E0101",
            "name": "外食",
            "share": 12.5
          }
        ],
        "code": "E01",
        "name": "餐飲",
        "share": 29.1,
        "type": "Floating"
      }
    ],
    "fixed_total": 60000.0,
    "floating_total": 84000.0,
    "total": 144000.0
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
