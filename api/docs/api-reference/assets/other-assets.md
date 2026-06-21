# Assets — Other Assets

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /assets/other-assets

**List asset categories**

Return all asset categories ordered by asset_index ascending (drives dropdown order).

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
| asset_id | string | yes | Asset category business ID |
| asset_name | string | yes | Display name |
| asset_type | string | yes | Asset category type |
| in_use | string | yes | Active flag |
| asset_index | integer | yes | Dropdown order |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "asset_id": "AC-STK-001",
      "asset_index": 1,
      "asset_name": "US equities",
      "asset_type": "stock",
      "in_use": "Y"
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

### POST /assets/other-assets

**Create asset category**

Create a new asset category. If asset_index is omitted, the server assigns max(asset_index)+1.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| asset_id | string | yes | Asset category business ID |
| asset_name | string | yes | Display name |
| asset_type | string | yes | Asset category type |
| in_use | string | yes | Active flag |
| asset_index |  | no | Display order; server assigns max+1 if omitted |

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
| asset_id | string | yes | Asset category business ID |
| asset_name | string | yes | Display name |
| asset_type | string | yes | Asset category type |
| in_use | string | yes | Active flag |
| asset_index | integer | yes | Dropdown order |

Example:

```json
{
  "status": 1,
  "data": {
    "asset_id": "AC-STK-001",
    "asset_index": 1,
    "asset_name": "US equities",
    "asset_type": "stock",
    "in_use": "Y"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 409 | Duplicate asset_id | `{"status": 0, "error": "Duplicate asset_id", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### GET /assets/other-assets/items

**List distinct asset types**

Return the distinct asset_type values currently in use.

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
| asset_type | string | yes | Distinct asset_type value |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "asset_type": "stock"
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

### DELETE /assets/other-assets/{asset_id}

**Delete asset category**

Delete an asset category by id.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| asset_id | path | string | yes |  |

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
| 404 | Asset not found | `{"status": 0, "error": "Asset not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### PUT /assets/other-assets/{asset_id}

**Update asset category**

Update an asset category by id; any omitted field is left unchanged.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| asset_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| asset_name |  | no | Display name |
| asset_type |  | no | Asset category type |
| in_use |  | no | Active flag |
| asset_index |  | no | Dropdown order |

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
| asset_id | string | yes | Asset category business ID |
| asset_name | string | yes | Display name |
| asset_type | string | yes | Asset category type |
| in_use | string | yes | Active flag |
| asset_index | integer | yes | Dropdown order |

Example:

```json
{
  "status": 1,
  "data": {
    "asset_id": "AC-STK-001",
    "asset_index": 1,
    "asset_name": "US equities",
    "asset_type": "stock",
    "in_use": "Y"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Asset not found | `{"status": 0, "error": "Asset not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
