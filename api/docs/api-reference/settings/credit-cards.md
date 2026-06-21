# Settings — Credit Cards

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /settings/credit-cards

**List credit cards**

List credit cards with optional filters on card_name (substring) and in_use. Ordered by credit_card_index ASC.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| card_name | query |  | no | Card name substring filter |
| in_use | query |  | no | Active flag filter Y/N |

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
| credit_card_id | string | yes | Business identifier |
| card_name | string | yes | Display name |
| card_no |  | no | Card number |
| last_day |  | no | Statement cut-off day |
| charge_day |  | no | Charge day |
| limit_date |  | no | Payment due day |
| card_expiry |  | no | Card expiration year/month 'YYYY/MM' |
| feedback_way |  | no | Rewards method |
| fx_code | string | yes | Billing currency code |
| in_use | string | yes | Active flag |
| credit_card_index | integer | yes | Dropdown order |
| note |  | no | Free-form note |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "card_expiry": "2026/08",
      "card_name": "Chase Sapphire",
      "card_no": "4111-XXXX-XXXX-1111",
      "charge_day": 15,
      "credit_card_id": "CC-VISA-01",
      "credit_card_index": 1,
      "feedback_way": "cashback",
      "fx_code": "USD",
      "in_use": "Y",
      "last_day": 25,
      "limit_date": 20,
      "note": "Primary card"
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

### POST /settings/credit-cards

**Create credit card**

Create a credit card. When credit_card_index is omitted, auto-fill with max(credit_card_index)+1.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| credit_card_id | string | yes | Business identifier |
| card_name | string | yes | Display name |
| card_no |  | no | Card number |
| last_day |  | no | Statement cut-off day |
| charge_day |  | no | Charge day |
| limit_date |  | no | Payment due day |
| card_expiry |  | no | Card expiration year/month 'YYYY/MM' |
| feedback_way |  | no | Rewards method |
| fx_code | string | yes | Billing currency code |
| in_use | string | no | Active flag |
| credit_card_index |  | no | Sort order; auto-filled with max+1 when omitted |
| note |  | no | Free-form note |

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
| credit_card_id | string | yes | Business identifier |
| card_name | string | yes | Display name |
| card_no |  | no | Card number |
| last_day |  | no | Statement cut-off day |
| charge_day |  | no | Charge day |
| limit_date |  | no | Payment due day |
| card_expiry |  | no | Card expiration year/month 'YYYY/MM' |
| feedback_way |  | no | Rewards method |
| fx_code | string | yes | Billing currency code |
| in_use | string | yes | Active flag |
| credit_card_index | integer | yes | Dropdown order |
| note |  | no | Free-form note |

Example:

```json
{
  "status": 1,
  "data": {
    "card_expiry": "2026/08",
    "card_name": "Chase Sapphire",
    "card_no": "4111-XXXX-XXXX-1111",
    "charge_day": 15,
    "credit_card_id": "CC-VISA-01",
    "credit_card_index": 1,
    "feedback_way": "cashback",
    "fx_code": "USD",
    "in_use": "Y",
    "last_day": 25,
    "limit_date": 20,
    "note": "Primary card"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 409 | Duplicate credit_card_id | `{"status": 0, "error": "Duplicate credit_card_id", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### DELETE /settings/credit-cards/{credit_card_id}

**Delete credit card**

Delete a credit card by credit_card_id. Returns 404 if not found.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| credit_card_id | path | string | yes |  |

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
| 404 | Credit card not found | `{"status": 0, "error": "Credit card 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### PUT /settings/credit-cards/{credit_card_id}

**Update credit card**

Update a credit card by credit_card_id. Returns 404 if not found.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| credit_card_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| card_name |  | no | Display name |
| card_no |  | no | Card number |
| last_day |  | no | Statement cut-off day |
| charge_day |  | no | Charge day |
| limit_date |  | no | Payment due day |
| card_expiry |  | no | Card expiration year/month 'YYYY/MM' |
| feedback_way |  | no | Rewards method |
| fx_code |  | no | Billing currency code |
| in_use |  | no | Active flag |
| credit_card_index |  | no | Dropdown order |
| note |  | no | Free-form note |

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
| credit_card_id | string | yes | Business identifier |
| card_name | string | yes | Display name |
| card_no |  | no | Card number |
| last_day |  | no | Statement cut-off day |
| charge_day |  | no | Charge day |
| limit_date |  | no | Payment due day |
| card_expiry |  | no | Card expiration year/month 'YYYY/MM' |
| feedback_way |  | no | Rewards method |
| fx_code | string | yes | Billing currency code |
| in_use | string | yes | Active flag |
| credit_card_index | integer | yes | Dropdown order |
| note |  | no | Free-form note |

Example:

```json
{
  "status": 1,
  "data": {
    "card_expiry": "2026/08",
    "card_name": "Chase Sapphire",
    "card_no": "4111-XXXX-XXXX-1111",
    "charge_day": 15,
    "credit_card_id": "CC-VISA-01",
    "credit_card_index": 1,
    "feedback_way": "cashback",
    "fx_code": "USD",
    "in_use": "Y",
    "last_day": 25,
    "limit_date": 20,
    "note": "Primary card"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Credit card not found | `{"status": 0, "error": "Credit card 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
