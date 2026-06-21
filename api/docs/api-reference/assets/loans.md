# Assets — Loans

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /assets/loans

**List loans**

Return all loan liabilities ordered by loan_index.

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
| loan_id | string | yes | Loan business ID |
| loan_name | string | yes | Loan display name |
| loan_type | string | yes | Loan type |
| account_id | string | yes | Repayment account business ID |
| account_name | string | yes | Repayment account display name |
| interest_rate | number | yes | Annual interest rate |
| period | integer | yes | Loan period in months |
| apply_date | string | yes | YYYYMMDD |
| grace_expire_date |  | no | Grace period end |
| pay_day | integer | yes | Day of month for repayment |
| amount | number | yes | Original loan amount |
| repayed | number | yes | Cumulative principal repaid |
| loan_index | integer | yes | Dropdown order |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "account_id": "BANK-CHASE-01",
      "account_name": "Chase Checking",
      "amount": 250000.0,
      "apply_date": "20200101",
      "grace_expire_date": "20200401",
      "interest_rate": 0.035,
      "loan_id": "LN-001",
      "loan_index": 1,
      "loan_name": "Mortgage",
      "loan_type": "mortgage",
      "pay_day": 1,
      "period": 360,
      "repayed": 12500.0
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

### POST /assets/loans

**Create loan**

Create a new loan liability; dates accept ISO 8601 and are stored as YYYYMMDD.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| loan_id | string | yes | Loan business ID |
| loan_name | string | yes | Loan display name |
| loan_type | string | yes | Loan type |
| account_id | string | yes | Repayment account business ID |
| account_name | string | yes | Repayment account display name |
| interest_rate | number | yes | Annual interest rate |
| period | integer | yes | Loan period in months |
| apply_date | string | yes | YYYYMMDD |
| grace_expire_date |  | no | Grace period end |
| pay_day | integer | yes | Day of month for repayment |
| amount | number | yes | Original loan amount |
| repayed | number | yes | Cumulative principal repaid |
| loan_index | integer | yes | Dropdown order |

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
| loan_id | string | yes | Loan business ID |
| loan_name | string | yes | Loan display name |
| loan_type | string | yes | Loan type |
| account_id | string | yes | Repayment account business ID |
| account_name | string | yes | Repayment account display name |
| interest_rate | number | yes | Annual interest rate |
| period | integer | yes | Loan period in months |
| apply_date | string | yes | YYYYMMDD |
| grace_expire_date |  | no | Grace period end |
| pay_day | integer | yes | Day of month for repayment |
| amount | number | yes | Original loan amount |
| repayed | number | yes | Cumulative principal repaid |
| loan_index | integer | yes | Dropdown order |

Example:

```json
{
  "status": 1,
  "data": {
    "account_id": "BANK-CHASE-01",
    "account_name": "Chase Checking",
    "amount": 250000.0,
    "apply_date": "20200101",
    "grace_expire_date": "20200401",
    "interest_rate": 0.035,
    "loan_id": "LN-001",
    "loan_index": 1,
    "loan_name": "Mortgage",
    "loan_type": "mortgage",
    "pay_day": 1,
    "period": 360,
    "repayed": 12500.0
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 409 | Duplicate loan_id | `{"status": 0, "error": "Duplicate loan_id", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### DELETE /assets/loans/{loan_id}

**Delete loan**

Delete a loan by id.

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
| 404 | Loan not found | `{"status": 0, "error": "Loan 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### GET /assets/loans/{loan_id}

**Get loan**

Return a single loan by id.

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

data:

| name | type | required | description |
| --- | --- | --- | --- |
| loan_id | string | yes | Loan business ID |
| loan_name | string | yes | Loan display name |
| loan_type | string | yes | Loan type |
| account_id | string | yes | Repayment account business ID |
| account_name | string | yes | Repayment account display name |
| interest_rate | number | yes | Annual interest rate |
| period | integer | yes | Loan period in months |
| apply_date | string | yes | YYYYMMDD |
| grace_expire_date |  | no | Grace period end |
| pay_day | integer | yes | Day of month for repayment |
| amount | number | yes | Original loan amount |
| repayed | number | yes | Cumulative principal repaid |
| loan_index | integer | yes | Dropdown order |

Example:

```json
{
  "status": 1,
  "data": {
    "account_id": "BANK-CHASE-01",
    "account_name": "Chase Checking",
    "amount": 250000.0,
    "apply_date": "20200101",
    "grace_expire_date": "20200401",
    "interest_rate": 0.035,
    "loan_id": "LN-001",
    "loan_index": 1,
    "loan_name": "Mortgage",
    "loan_type": "mortgage",
    "pay_day": 1,
    "period": 360,
    "repayed": 12500.0
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

### PUT /assets/loans/{loan_id}

**Update loan**

Update a loan; repayed is server-computed and cannot be set via this endpoint.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| loan_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| loan_name |  | no | Loan display name |
| loan_type |  | no | Loan type |
| account_id |  | no | Repayment account business ID |
| account_name |  | no | Repayment account display name |
| interest_rate |  | no | Annual interest rate |
| period |  | no | Loan period in months |
| apply_date |  | no | YYYYMMDD |
| grace_expire_date |  | no | Grace period end |
| pay_day |  | no | Day of month for repayment |
| amount |  | no | Original loan amount |
| repayed |  | no | Cumulative principal repaid |
| loan_index |  | no | Dropdown order |

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
| loan_id | string | yes | Loan business ID |
| loan_name | string | yes | Loan display name |
| loan_type | string | yes | Loan type |
| account_id | string | yes | Repayment account business ID |
| account_name | string | yes | Repayment account display name |
| interest_rate | number | yes | Annual interest rate |
| period | integer | yes | Loan period in months |
| apply_date | string | yes | YYYYMMDD |
| grace_expire_date |  | no | Grace period end |
| pay_day | integer | yes | Day of month for repayment |
| amount | number | yes | Original loan amount |
| repayed | number | yes | Cumulative principal repaid |
| loan_index | integer | yes | Dropdown order |

Example:

```json
{
  "status": 1,
  "data": {
    "account_id": "BANK-CHASE-01",
    "account_name": "Chase Checking",
    "amount": 250000.0,
    "apply_date": "20200101",
    "grace_expire_date": "20200401",
    "interest_rate": 0.035,
    "loan_id": "LN-001",
    "loan_index": 1,
    "loan_name": "Mortgage",
    "loan_type": "mortgage",
    "pay_day": 1,
    "period": 360,
    "repayed": 12500.0
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
