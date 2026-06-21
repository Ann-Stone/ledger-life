# Assets — Loans Selection

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /assets/loans/selection

**Loan dropdown options**

Return id/name pairs for loan selection UIs.

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
| loan_id | string | yes | Loan business ID |
| loan_name | string | yes | Loan display name |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "loan_id": "LN-001",
      "loan_name": "Mortgage"
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
