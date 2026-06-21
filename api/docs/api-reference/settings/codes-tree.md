# Settings — Codes Tree

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /settings/codes/all-with-sub

**Full code tree**

Return all main codes with their sub-codes nested under sub_codes.

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
| code_id | string | yes | Business identifier |
| code_type | string | yes | code type |
| name | string | yes | Display name |
| parent_id |  | no | Parent code_id |
| in_use | string | yes | Active flag |
| code_index | integer | yes | Dropdown order |
| is_annual_event | boolean | no | Budget as a single annual envelope |
| sub_codes | array<CodeDataRead> | no | Nested sub-codes |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "code_id": "E01",
      "code_index": 1,
      "code_type": "Floating",
      "in_use": "Y",
      "is_annual_event": false,
      "name": "Food",
      "sub_codes": []
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

### GET /settings/codes/{parent_id}/sub-codes

**List sub-codes of a parent**

List sub-codes belonging to a main code, ordered by code_index.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| parent_id | path | string | yes |  |

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
| code_id | string | yes | Business identifier |
| code_type | string | yes | code type |
| name | string | yes | Display name |
| parent_id |  | no | Parent code_id |
| in_use | string | yes | Active flag |
| code_index | integer | yes | Dropdown order |
| is_annual_event | boolean | no | Budget as a single annual envelope |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "code_id": "E01",
      "code_index": 1,
      "code_type": "Floating",
      "in_use": "Y",
      "is_annual_event": false,
      "name": "Food"
    }
  ],
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Parent code not found | `{"status": 0, "error": "Parent code 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
