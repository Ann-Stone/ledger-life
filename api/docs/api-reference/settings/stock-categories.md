# Settings — Stock Categories

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /settings/stock-categories

**List stock categories**

List stock allocation categories ordered by category_index.

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
| category_id | string | yes | Category business ID |
| name | string | yes | Display name |
| in_use | string | yes | Active flag (Y/N) |
| category_index | integer | yes | Dropdown order |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "category_id": "SC-001",
      "category_index": 1,
      "in_use": "Y",
      "name": "成長型"
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

### POST /settings/stock-categories

**Create stock category**

Create a stock category. The category_id is generated server-side (SC-NNN).

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| name | string | yes | Display name |
| in_use | string | no | Active flag (Y/N) |
| category_index |  | no | Display order; server assigns max+1 when omitted |

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
| category_id | string | yes | Category business ID |
| name | string | yes | Display name |
| in_use | string | yes | Active flag (Y/N) |
| category_index | integer | yes | Dropdown order |

Example:

```json
{
  "status": 1,
  "data": {
    "category_id": "SC-001",
    "category_index": 1,
    "in_use": "Y",
    "name": "成長型"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### DELETE /settings/stock-categories/{category_id}

**Delete stock category**

Delete a stock category by id. Refused with 409 when any holding still references it — retire it with in_use='N' instead.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| category_id | path | string | yes |  |

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
| 404 | Stock category not found | `{"status": 0, "error": "Stock category 42 not found", "msg": "fail"}` |
| 409 | Category in use | `{"status": 0, "error": "Stock category SC-001 is in use by one or more holdings", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### PUT /settings/stock-categories/{category_id}

**Update stock category**

Update a stock category by id. Set in_use='N' to retire it. Returns 404 if not found.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| category_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| name |  | no | Display name |
| in_use |  | no | Active flag (Y/N); set 'N' to retire a category |
| category_index |  | no | Dropdown order |

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
| category_id | string | yes | Category business ID |
| name | string | yes | Display name |
| in_use | string | yes | Active flag (Y/N) |
| category_index | integer | yes | Dropdown order |

Example:

```json
{
  "status": 1,
  "data": {
    "category_id": "SC-001",
    "category_index": 1,
    "in_use": "Y",
    "name": "成長型"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Stock category not found | `{"status": 0, "error": "Stock category 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
