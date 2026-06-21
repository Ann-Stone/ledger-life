# Monthly Report — Insurance Values

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### POST /monthly-report/insurance-values

**Record (insert or update) a policy's surrender value for a month**

Upsert the 解約金 for a (policy, month). Idempotent on the composite key; 404 when the policy does not exist.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| insurance_id | string | yes | FK to Insurance.insurance_id |
| vesting_month | string | yes | YYYYMM the value is effective from |
| surrender_value | number | yes | 解約金 in policy currency |
| memo |  | no | Free-form memo |

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
| insurance_id | string | yes | FK to Insurance.insurance_id |
| vesting_month | string | yes | YYYYMM the value is effective from |
| surrender_value | number | yes | 解約金 in policy currency |
| memo |  | no | Free-form memo |

Example:

```json
{
  "status": 1,
  "data": {
    "insurance_id": "INS-001",
    "memo": "保單第 6 年度解約金",
    "surrender_value": 185000.0,
    "vesting_month": "202604"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Insurance not found | `{"status": 0, "error": "Insurance 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### GET /monthly-report/insurance-values/{vesting_month}

**Month-level surrender values for every policy**

For every insurance policy, return the latest recorded surrender value (解約金) on or before month-end (carried forward), with a ``recorded`` flag that is true only when entered in this exact month.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| vesting_month | path | string | yes | YYYYMM |

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
| insurance_id | string | yes | Policy business ID |
| insurance_name | string | yes | Policy display name |
| surrender_value |  | no | Latest recorded 解約金 on or before the month, or null when none recorded |
| vesting_month |  | no | YYYYMM the surrender_value was recorded for, or null when none |
| recorded | boolean | no | True when a value was recorded in this exact month (not carried forward) |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "insurance_id": "INS-001",
      "insurance_name": "Whole life policy",
      "recorded": true,
      "surrender_value": 185000.0,
      "vesting_month": "202604"
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
