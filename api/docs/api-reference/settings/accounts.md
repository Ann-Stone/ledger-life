# Settings — Accounts

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /settings/accounts

**List accounts**

List accounts with optional filters on name, account_type, in_use.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| name | query |  | no | Name substring filter |
| account_type | query |  | no | Account type filter |
| in_use | query |  | no | In-use flag filter |

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
| id | integer | yes | Autoincrement PK |
| account_id | string | yes | Business identifier |
| name | string | yes | Account name |
| account_type | string | yes | Account type |
| fx_code | string | yes | Currency code |
| is_calculate | string | yes | Include in totals (Y/N) |
| in_use | string | yes | Active flag (Y/N) |
| discount | number | yes | Discount multiplier |
| memo |  | no | Free-form memo |
| owner |  | no | Owner label |
| account_index | integer | yes | Dropdown order |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "account_id": "BANK-CHASE-01",
      "account_index": 1,
      "account_type": "bank",
      "discount": 1.0,
      "fx_code": "USD",
      "id": 1,
      "in_use": "Y",
      "is_calculate": "Y",
      "memo": "Primary checking",
      "name": "Chase Checking",
      "owner": "stone"
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

### POST /settings/accounts

**Create account**

Create an account. Rejects 422 when account_id is missing; 409 when account_id duplicates existing row.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| account_id | string | yes | User-supplied business identifier |
| name | string | yes | Account name |
| account_type | string | yes | Account type |
| fx_code | string | yes | Currency code |
| is_calculate | string | no | Include in totals (Y/N) |
| in_use | string | no | Active flag (Y/N) |
| discount | number | no | Discount multiplier |
| memo |  | no | Free-form memo |
| owner |  | no | Owner label |
| account_index |  | no | Optional sort order; auto-filled with max(account_index)+1 when omitted |

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
| id | integer | yes | Autoincrement PK |
| account_id | string | yes | Business identifier |
| name | string | yes | Account name |
| account_type | string | yes | Account type |
| fx_code | string | yes | Currency code |
| is_calculate | string | yes | Include in totals (Y/N) |
| in_use | string | yes | Active flag (Y/N) |
| discount | number | yes | Discount multiplier |
| memo |  | no | Free-form memo |
| owner |  | no | Owner label |
| account_index | integer | yes | Dropdown order |

Example:

```json
{
  "status": 1,
  "data": {
    "account_id": "BANK-CHASE-01",
    "account_index": 1,
    "account_type": "bank",
    "discount": 1.0,
    "fx_code": "USD",
    "id": 1,
    "in_use": "Y",
    "is_calculate": "Y",
    "memo": "Primary checking",
    "name": "Chase Checking",
    "owner": "stone"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 409 | Duplicate account_id | `{"status": 0, "error": "Account with account_id 'BANK-CHASE-01' already exists", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### GET /settings/accounts/selection

**Active accounts for dropdown**

Return in-use accounts ordered by account_index ASC for use in dropdowns.

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
| id | integer | yes | Autoincrement PK |
| account_id | string | yes | Business identifier |
| name | string | yes | Account name |
| account_type | string | yes | Account type |
| fx_code | string | yes | Currency code |
| is_calculate | string | yes | Include in totals (Y/N) |
| in_use | string | yes | Active flag (Y/N) |
| discount | number | yes | Discount multiplier |
| memo |  | no | Free-form memo |
| owner |  | no | Owner label |
| account_index | integer | yes | Dropdown order |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "account_id": "BANK-CHASE-01",
      "account_index": 1,
      "account_type": "bank",
      "discount": 1.0,
      "fx_code": "USD",
      "id": 1,
      "in_use": "Y",
      "is_calculate": "Y",
      "memo": "Primary checking",
      "name": "Chase Checking",
      "owner": "stone"
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

### DELETE /settings/accounts/{id}

**Delete account**

Delete an account by autoincrement id. Returns 404 if id not found.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| id | path | integer | yes |  |

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
| 404 | Account not found | `{"status": 0, "error": "Account 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### PUT /settings/accounts/{id}

**Update account**

Update an account by autoincrement id. Returns 404 if id not found.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| id | path | integer | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| account_id |  | no | Business identifier |
| name |  | no | Account name |
| account_type |  | no | Account type |
| fx_code |  | no | Currency code |
| is_calculate |  | no | Include in totals (Y/N) |
| in_use |  | no | Active flag (Y/N) |
| discount |  | no | Discount multiplier |
| memo |  | no | Free-form memo |
| owner |  | no | Owner label |
| account_index |  | no | Dropdown order |

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
| id | integer | yes | Autoincrement PK |
| account_id | string | yes | Business identifier |
| name | string | yes | Account name |
| account_type | string | yes | Account type |
| fx_code | string | yes | Currency code |
| is_calculate | string | yes | Include in totals (Y/N) |
| in_use | string | yes | Active flag (Y/N) |
| discount | number | yes | Discount multiplier |
| memo |  | no | Free-form memo |
| owner |  | no | Owner label |
| account_index | integer | yes | Dropdown order |

Example:

```json
{
  "status": 1,
  "data": {
    "account_id": "BANK-CHASE-01",
    "account_index": 1,
    "account_type": "bank",
    "discount": 1.0,
    "fx_code": "USD",
    "id": 1,
    "in_use": "Y",
    "is_calculate": "Y",
    "memo": "Primary checking",
    "name": "Chase Checking",
    "owner": "stone"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Account not found | `{"status": 0, "error": "Account 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
