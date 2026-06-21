# Settings — Sub Codes

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### POST /settings/sub-codes

**Create sub-code**

Create a sub-code. parent_id must reference an existing main code (404 otherwise).

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| code_id | string | yes | Business identifier |
| code_type | string | yes | Code category: Fixed / Floating / Invest / Income / Transfer / etc. |
| name | string | yes | Display name |
| parent_id |  | no | Parent code_id; null for main codes |
| in_use | string | no | Active flag |
| code_index |  | no | Dropdown order; auto-filled with max+1 when omitted |
| is_annual_event | boolean | no | Budget as a single annual envelope |

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
  "data": {
    "code_id": "E01",
    "code_index": 1,
    "code_type": "Floating",
    "in_use": "Y",
    "is_annual_event": false,
    "name": "Food"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Parent code not found | `{"status": 0, "error": "Parent code 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### DELETE /settings/sub-codes/{code_id}

**Delete sub-code**

Delete a sub-code by code_id. Returns 404 if not found. No cascading.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| code_id | path | string | yes |  |

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
| 404 | Sub-code not found | `{"status": 0, "error": "Sub-code 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### PUT /settings/sub-codes/{code_id}

**Update sub-code**

Update a sub-code by code_id. Returns 404 if not found.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| code_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| code_type |  | no | code type |
| name |  | no | Display name |
| parent_id |  | no | Parent code_id |
| in_use |  | no | Active flag |
| code_index |  | no | Dropdown order |
| is_annual_event |  | no | Budget as a single annual envelope |

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
  "data": {
    "code_id": "E01",
    "code_index": 1,
    "code_type": "Floating",
    "in_use": "Y",
    "is_annual_event": false,
    "name": "Food"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Sub-code not found | `{"status": 0, "error": "Sub-code 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
