# Dashboard — Alarms

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /dashboard/alarms

**List upcoming alarms**

Returns alarms scheduled within today..today+6 months. Monthly-recurring alarms are expanded per month; expired months are excluded.

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
| date | string | yes | Expanded occurrence date in YYYYMMDD |
| content | string | yes | Alarm content |
| alarm_type | string (enum: 'Y', 'M') | yes | Recurrence type: 'Y' yearly, 'M' monthly |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "alarm_type": "Y",
      "content": "報稅",
      "date": "20260531"
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
