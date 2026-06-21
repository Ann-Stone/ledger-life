# Settings — Alarms

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /settings/alarms

**List all alarms**

List every alarm ordered by alarm_id ASC.

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
| alarm_id | integer | yes | Autoincrement PK |
| alarm_type | string (enum: 'Y', 'M') | yes | Recurrence: 'Y' yearly, 'M' monthly |
| alarm_date | string | yes | Recurring anchor: MMDD for Y, DD for M |
| content | string | yes | Reminder text |
| due_date |  | no | Optional YYYYMM cutoff |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "alarm_date": "0531",
      "alarm_id": 1,
      "alarm_type": "Y",
      "content": "報稅"
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

### POST /settings/alarms

**Create alarm**

Create an alarm. due_date accepts multiple formats (ISO 8601, YYYY-MM-DD, YYYYMMDD) and is persisted normalized as YYYYMMDD.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| alarm_type | string (enum: 'Y', 'M') | yes | Recurrence: 'Y' yearly, 'M' monthly |
| alarm_date | string | yes | Recurring anchor: MMDD for Y, DD for M |
| content | string | yes | Reminder text |
| due_date |  | no | Optional YYYYMM cutoff |

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
| alarm_id | integer | yes | Autoincrement PK |
| alarm_type | string (enum: 'Y', 'M') | yes | Recurrence: 'Y' yearly, 'M' monthly |
| alarm_date | string | yes | Recurring anchor: MMDD for Y, DD for M |
| content | string | yes | Reminder text |
| due_date |  | no | Optional YYYYMM cutoff |

Example:

```json
{
  "status": 1,
  "data": {
    "alarm_date": "0531",
    "alarm_id": 1,
    "alarm_type": "Y",
    "content": "報稅"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### GET /settings/alarms/by-date

**List alarms matching a date**

Return alarms whose alarm_date equals the query date (e.g. 08/26) or ends with it (e.g. monthly day 26 matches).

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| date | query | string | yes | Date in MM/DD or DD form |

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
| alarm_id | integer | yes | Autoincrement PK |
| alarm_type | string (enum: 'Y', 'M') | yes | Recurrence: 'Y' yearly, 'M' monthly |
| alarm_date | string | yes | Recurring anchor: MMDD for Y, DD for M |
| content | string | yes | Reminder text |
| due_date |  | no | Optional YYYYMM cutoff |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "alarm_date": "0531",
      "alarm_id": 1,
      "alarm_type": "Y",
      "content": "報稅"
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

### DELETE /settings/alarms/{alarm_id}

**Delete alarm**

Delete an alarm by alarm_id. Returns 404 if not found.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| alarm_id | path | integer | yes |  |

#### Response (200)

Envelope:

| name | type | required | description |
| --- | --- | --- | --- |
| status | integer | no | 1 = success, 0 = fail |
| data |  | no | Response payload. Shape depends on the endpoint. |
| msg | string | no | Human-readable status message |

Example:

```json
{
  "status": 1,
  "data": null,
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Alarm not found | `{"status": 0, "error": "Alarm 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### PUT /settings/alarms/{alarm_id}

**Update alarm**

Update an alarm by alarm_id. Returns 404 if not found. due_date is re-normalized when provided.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| alarm_id | path | integer | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| alarm_type |  | no | Recurrence: 'Y' yearly, 'M' monthly |
| alarm_date |  | no | Recurring anchor: MMDD for Y, DD for M |
| content |  | no | Reminder text |
| due_date |  | no | Optional YYYYMM cutoff |

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
| alarm_id | integer | yes | Autoincrement PK |
| alarm_type | string (enum: 'Y', 'M') | yes | Recurrence: 'Y' yearly, 'M' monthly |
| alarm_date | string | yes | Recurring anchor: MMDD for Y, DD for M |
| content | string | yes | Reminder text |
| due_date |  | no | Optional YYYYMM cutoff |

Example:

```json
{
  "status": 1,
  "data": {
    "alarm_date": "0531",
    "alarm_id": 1,
    "alarm_type": "Y",
    "content": "報稅"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Alarm not found | `{"status": 0, "error": "Alarm 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
