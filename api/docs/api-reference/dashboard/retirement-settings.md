# Dashboard — Retirement Settings

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /dashboard/retirement-settings

**Get retirement settings**

Returns the withdrawal rate (default 4%) and optional expense-base override.

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
| withdrawal_rate | number | yes | Safe withdrawal rate (decimal) |
| annual_expense_override |  | no | Manual annual expense base (TWD), or null to auto-compute |
| exclude_self_occupied_estate | boolean | no | Exclude self-occupied (estate_status 'live') housing from retirement net worth |

Example:

```json
{
  "status": 1,
  "data": {
    "exclude_self_occupied_estate": true,
    "withdrawal_rate": 0.04
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### PUT /dashboard/retirement-settings

**Update retirement settings**

Upsert the single config row. withdrawal_rate (0.001–0.5) is optional; annual_expense_override is set verbatim (null clears it).

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| withdrawal_rate |  | no | New withdrawal rate (decimal, 0.01–0.10); null keeps current |
| annual_expense_override |  | no | New manual expense base (TWD); null keeps current. Send 0 to clear. |
| exclude_self_occupied_estate |  | no | Toggle excluding self-occupied housing; null keeps current |

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
| withdrawal_rate | number | yes | Safe withdrawal rate (decimal) |
| annual_expense_override |  | no | Manual annual expense base (TWD), or null to auto-compute |
| exclude_self_occupied_estate | boolean | no | Exclude self-occupied (estate_status 'live') housing from retirement net worth |

Example:

```json
{
  "status": 1,
  "data": {
    "exclude_self_occupied_estate": true,
    "withdrawal_rate": 0.04
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
