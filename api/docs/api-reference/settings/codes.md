# Settings — Codes

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /settings/codes

**List main codes**

List all main (top-level) codes ordered by code_index.

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
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### POST /settings/codes

**Create main code**

Create a main code. If code_type is Fixed or Floating, a Budget row for the current year is auto-inserted with all monthly amounts set to 0.

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
| 409 | Duplicate code_id | `{"status": 0, "error": "Duplicate code_id", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### DELETE /settings/codes/{code_id}

**Delete main code**

Delete a main code by code_id. Returns 404 if not found.

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
| 404 | Code not found | `{"status": 0, "error": "Code 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### PUT /settings/codes/{code_id}

**Update main code**

Update a main code by code_id. Returns 404 if not found.

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
| 404 | Code not found | `{"status": 0, "error": "Code 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
