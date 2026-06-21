# Assets — Estates Details

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### DELETE /assets/estates/details/{distinct_number}

**Delete estate transaction**

Delete a single estate transaction row.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| distinct_number | path | integer | yes |  |

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
| 404 | Transaction not found | `{"status": 0, "error": "Transaction not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### PUT /assets/estates/details/{distinct_number}

**Update estate transaction**

Update a single estate transaction row.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| distinct_number | path | integer | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| estate_excute_type |  | no | Transaction type |
| excute_price |  | no | Amount |
| excute_date |  | no | YYYYMMDD |
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
| distinct_number | integer | yes | Autoincrement PK |
| estate_id | string | yes | FK to Estate.estate_id |
| estate_excute_type | string | yes | Transaction type |
| excute_price | number | yes | Amount |
| excute_date | string | yes | YYYYMMDD |
| memo |  | no | Free-form memo |

Example:

```json
{
  "status": 1,
  "data": {
    "distinct_number": 1,
    "estate_excute_type": "tax",
    "estate_id": "EST-001",
    "excute_date": "20200101",
    "excute_price": 500000.0,
    "memo": "Closing"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Transaction not found | `{"status": 0, "error": "Transaction not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### GET /assets/estates/{estate_id}/details

**List estate transactions**

Return all fee/tax/rent/deposit transactions for an estate property.

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

data (array item):

| name | type | required | description |
| --- | --- | --- | --- |
| distinct_number | integer | yes | Autoincrement PK |
| estate_id | string | yes | FK to Estate.estate_id |
| estate_excute_type | string | yes | Transaction type |
| excute_price | number | yes | Amount |
| excute_date | string | yes | YYYYMMDD |
| memo |  | no | Free-form memo |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "distinct_number": 1,
      "estate_excute_type": "tax",
      "estate_id": "EST-001",
      "excute_date": "20200101",
      "excute_price": 500000.0,
      "memo": "Closing"
    }
  ],
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Estate not found | `{"status": 0, "error": "Estate 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### POST /assets/estates/{estate_id}/details

**Record estate transaction**

Record a tax/fee/insurance/fix/rent/deposit transaction.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| estate_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| estate_id | string | yes | FK to Estate.estate_id |
| estate_excute_type | string (enum: 'tax', 'fee', 'insurance', 'fix', 'rent', 'deposit') | yes | tax/fee/insurance/fix/rent/deposit |
| excute_price | number | yes | Amount |
| excute_date | string | yes | YYYYMMDD |
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
| distinct_number | integer | yes | Autoincrement PK |
| estate_id | string | yes | FK to Estate.estate_id |
| estate_excute_type | string | yes | Transaction type |
| excute_price | number | yes | Amount |
| excute_date | string | yes | YYYYMMDD |
| memo |  | no | Free-form memo |

Example:

```json
{
  "status": 1,
  "data": {
    "distinct_number": 1,
    "estate_excute_type": "tax",
    "estate_id": "EST-001",
    "excute_date": "20200101",
    "excute_price": 500000.0,
    "memo": "Closing"
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
