# Assets — Loans Details

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### DELETE /assets/loans/details/{distinct_number}

**Delete loan transaction**

Delete a single loan transaction row; Loan.repayed auto-recalculates.

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

### PUT /assets/loans/details/{distinct_number}

**Update loan transaction**

Update a single loan transaction row; Loan.repayed auto-recalculates.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| distinct_number | path | integer | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| loan_excute_type |  | no | Execution type |
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
| loan_id | string | yes | FK to Loan.loan_id |
| loan_excute_type | string | yes | Execution type |
| excute_price | number | yes | Amount |
| excute_date | string | yes | YYYYMMDD |
| memo |  | no | Free-form memo |

Example:

```json
{
  "status": 1,
  "data": {
    "distinct_number": 1,
    "excute_date": "20260401",
    "excute_price": 1500.0,
    "loan_excute_type": "repayment",
    "loan_id": "LN-001",
    "memo": "April payment"
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

### GET /assets/loans/{loan_id}/details

**List loan transactions**

Return all repayment / interest / fee / increment transactions for a loan.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| loan_id | path | string | yes |  |

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
| loan_id | string | yes | FK to Loan.loan_id |
| loan_excute_type | string | yes | Execution type |
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
      "excute_date": "20260401",
      "excute_price": 1500.0,
      "loan_excute_type": "repayment",
      "loan_id": "LN-001",
      "memo": "April payment"
    }
  ],
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Loan not found | `{"status": 0, "error": "Loan 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### POST /assets/loans/{loan_id}/details

**Record loan transaction**

Record a principal/interest/increment/fee transaction. Server auto-recalculates Loan.repayed on principal rows.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| loan_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| loan_id | string | yes | FK to Loan.loan_id |
| loan_excute_type | string (enum: 'principal', 'interest', 'increment', 'fee') | yes | principal/interest/increment/fee |
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
| loan_id | string | yes | FK to Loan.loan_id |
| loan_excute_type | string | yes | Execution type |
| excute_price | number | yes | Amount |
| excute_date | string | yes | YYYYMMDD |
| memo |  | no | Free-form memo |

Example:

```json
{
  "status": 1,
  "data": {
    "distinct_number": 1,
    "excute_date": "20260401",
    "excute_price": 1500.0,
    "loan_excute_type": "repayment",
    "loan_id": "LN-001",
    "memo": "April payment"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Loan not found | `{"status": 0, "error": "Loan 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
