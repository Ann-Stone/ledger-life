# Dashboard — Gifts

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /dashboard/gifts/{year}

**Gifted amounts by year**

Returns cross-owner Transfer totals grouped by sender (Account.owner). Rate is amount * 100 / 2,200,000 (legacy gift-tax threshold).

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| year | path | string | yes | YYYY |

#### Response (200)

Envelope:

| name | type | required | description |
| --- | --- | --- | --- |
| status | integer | no | 1 = success, 0 = fail |
| data |  | no | Response payload. Shape depends on the endpoint. |
| msg | string | no | Human-readable status message |

data (array item):

| name | type | required | description |
| --- | --- | --- | --- |
| owner | string | yes | Recipient/sender owner name from Account.owner |
| amount | number | yes | Summed absolute spending in base currency |
| rate | number | yes | amount * 100 / 2,200,000 (legacy gift-tax threshold percentage) |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "amount": 6000.0,
      "owner": "Mom",
      "rate": 0.27
    }
  ],
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
