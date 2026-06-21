# Health

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /health

**Server health check**

Returns alive=true and the running app version. Does not depend on the database.

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
| alive | boolean | yes | True when the API process is responsive |
| version | string | yes | Running app version (from pyproject.toml) |

Example:

```json
{
  "status": 1,
  "data": {
    "alive": true,
    "version": "1.0.0"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
