# Assets — Estates

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /assets/estates

**List real-estate holdings**

Return estate properties filtered by asset_id.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| asset_id | query | string | yes | Parent asset category id |

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
| estate_id | string | yes | Estate business ID |
| estate_name | string | yes | Estate display name |
| estate_type | string | yes | Estate type |
| estate_address | string | yes | Physical address |
| asset_id | string | yes | Asset category ID |
| fx_code | string | no | Currency code (TWD; USD/JPY/... for overseas property) |
| obtain_date | string | yes | YYYYMMDD |
| loan_id |  | no | Associated loan ID |
| estate_status | string | yes | Status |
| region |  | no | House-price-index 縣市 (全國/臺北市/新北市/桃園市/臺中市/臺南市/高雄市); null → 全國 |
| memo |  | no | Free-form memo |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "asset_id": "AC-REAL-001",
      "estate_address": "123 Main St",
      "estate_id": "EST-001",
      "estate_name": "Condo",
      "estate_status": "live",
      "estate_type": "residential",
      "fx_code": "TWD",
      "loan_id": "LN-001",
      "memo": "Primary residence",
      "obtain_date": "20200101",
      "region": "臺北市"
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

### POST /assets/estates

**Create real-estate holding**

Create a new estate property; obtain_date accepts ISO 8601 and is stored as YYYYMMDD.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| estate_id | string | yes | Estate business ID |
| estate_name | string | yes | Estate display name |
| estate_type | string | yes | Estate type |
| estate_address | string | yes | Physical address |
| asset_id | string | yes | Asset category ID |
| fx_code | string | no | Currency code (TWD; USD/JPY/... for overseas property) |
| obtain_date | string | yes | YYYYMMDD |
| loan_id |  | no | Associated loan ID |
| estate_status | string (enum: 'idle', 'live', 'rent', 'sold') | yes | Status |
| region |  | no | House-price-index 縣市 (全國/臺北市/新北市/桃園市/臺中市/臺南市/高雄市); null → 全國 |
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
| estate_id | string | yes | Estate business ID |
| estate_name | string | yes | Estate display name |
| estate_type | string | yes | Estate type |
| estate_address | string | yes | Physical address |
| asset_id | string | yes | Asset category ID |
| fx_code | string | no | Currency code (TWD; USD/JPY/... for overseas property) |
| obtain_date | string | yes | YYYYMMDD |
| loan_id |  | no | Associated loan ID |
| estate_status | string | yes | Status |
| region |  | no | House-price-index 縣市 (全國/臺北市/新北市/桃園市/臺中市/臺南市/高雄市); null → 全國 |
| memo |  | no | Free-form memo |

Example:

```json
{
  "status": 1,
  "data": {
    "asset_id": "AC-REAL-001",
    "estate_address": "123 Main St",
    "estate_id": "EST-001",
    "estate_name": "Condo",
    "estate_status": "live",
    "estate_type": "residential",
    "fx_code": "TWD",
    "loan_id": "LN-001",
    "memo": "Primary residence",
    "obtain_date": "20200101",
    "region": "臺北市"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 409 | Duplicate estate_id | `{"status": 0, "error": "Duplicate estate_id", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### DELETE /assets/estates/{estate_id}

**Delete real-estate holding**

Delete an estate property by id.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| estate_id | path | string | yes |  |

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
| 404 | Estate not found | `{"status": 0, "error": "Estate 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### PUT /assets/estates/{estate_id}

**Update real-estate holding**

Update an estate property; any omitted field is left unchanged.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| estate_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| estate_name |  | no | Estate display name |
| estate_type |  | no | Estate type |
| estate_address |  | no | Physical address |
| asset_id |  | no | Asset category ID |
| fx_code |  | no | Currency code (TWD; USD/JPY/... for overseas property) |
| obtain_date |  | no | YYYYMMDD |
| loan_id |  | no | Associated loan ID |
| estate_status |  | no | Status |
| region |  | no | House-price-index 縣市 (全國/臺北市/新北市/桃園市/臺中市/臺南市/高雄市); null → 全國 |
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
| estate_id | string | yes | Estate business ID |
| estate_name | string | yes | Estate display name |
| estate_type | string | yes | Estate type |
| estate_address | string | yes | Physical address |
| asset_id | string | yes | Asset category ID |
| fx_code | string | no | Currency code (TWD; USD/JPY/... for overseas property) |
| obtain_date | string | yes | YYYYMMDD |
| loan_id |  | no | Associated loan ID |
| estate_status | string | yes | Status |
| region |  | no | House-price-index 縣市 (全國/臺北市/新北市/桃園市/臺中市/臺南市/高雄市); null → 全國 |
| memo |  | no | Free-form memo |

Example:

```json
{
  "status": 1,
  "data": {
    "asset_id": "AC-REAL-001",
    "estate_address": "123 Main St",
    "estate_id": "EST-001",
    "estate_name": "Condo",
    "estate_status": "live",
    "estate_type": "residential",
    "fx_code": "TWD",
    "loan_id": "LN-001",
    "memo": "Primary residence",
    "obtain_date": "20200101",
    "region": "臺北市"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Estate not found | `{"status": 0, "error": "Estate 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
