# Assets — Insurances Details

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### DELETE /assets/insurances/details/{distinct_number}

**Delete insurance transaction**

Delete a single insurance transaction row.

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

### PUT /assets/insurances/details/{distinct_number}

**Update insurance transaction**

Update a single insurance transaction row.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| distinct_number | path | integer | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| insurance_excute_type |  | no | Execution type |
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
| insurance_id | string | yes | FK to Insurance.insurance_id |
| insurance_excute_type | string | yes | Execution type |
| excute_price | number | yes | Amount |
| excute_date | string | yes | YYYYMMDD |
| memo |  | no | Free-form memo |

Example:

```json
{
  "status": 1,
  "data": {
    "distinct_number": 1,
    "excute_date": "20260115",
    "excute_price": 1200.0,
    "insurance_excute_type": "pay",
    "insurance_id": "INS-001",
    "memo": "Annual premium"
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

### GET /assets/insurances/{insurance_id}/details

**List insurance transactions**

Return all premium/claim/return transactions for a policy.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| insurance_id | path | string | yes |  |

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
| insurance_id | string | yes | FK to Insurance.insurance_id |
| insurance_excute_type | string | yes | Execution type |
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
      "excute_date": "20260115",
      "excute_price": 1200.0,
      "insurance_excute_type": "pay",
      "insurance_id": "INS-001",
      "memo": "Annual premium"
    }
  ],
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Insurance not found | `{"status": 0, "error": "Insurance 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### POST /assets/insurances/{insurance_id}/details

**Record insurance premium/claim**

Record a pay/cash/return/expect transaction.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| insurance_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| insurance_id | string | yes | FK to Insurance.insurance_id |
| insurance_excute_type | string (enum: 'pay', 'cash', 'return', 'expect') | yes | pay/cash/return/expect |
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
| insurance_id | string | yes | FK to Insurance.insurance_id |
| insurance_excute_type | string | yes | Execution type |
| excute_price | number | yes | Amount |
| excute_date | string | yes | YYYYMMDD |
| memo |  | no | Free-form memo |

Example:

```json
{
  "status": 1,
  "data": {
    "distinct_number": 1,
    "excute_date": "20260115",
    "excute_price": 1200.0,
    "insurance_excute_type": "pay",
    "insurance_id": "INS-001",
    "memo": "Annual premium"
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
