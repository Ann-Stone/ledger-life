# Reports — Assets

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /reports/assets

**Get asset composition**

Returns share (% + absolute) of each asset type, FX-converted to base currency.

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
| total | number | yes | Total asset value in base currency |
| items | array<AssetShare> | yes | Per-bucket share, sums to 100% within rounding |

Example:

```json
{
  "status": 1,
  "data": {
    "items": [
      {
        "amount": 200000.0,
        "share": 32.5,
        "type": "stocks"
      },
      {
        "amount": 415384.62,
        "share": 67.5,
        "type": "accounts"
      }
    ],
    "total": 615384.62
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
