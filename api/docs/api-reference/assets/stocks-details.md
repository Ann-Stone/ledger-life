# Assets — Stocks Details

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### DELETE /assets/stocks/details/{distinct_number}

**Delete stock transaction**

Delete a single stock transaction row.

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

### PUT /assets/stocks/details/{distinct_number}

**Update stock transaction**

Update a single stock transaction row.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| distinct_number | path | integer | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| excute_type |  | no | Transaction type |
| excute_amount |  | no | Quantity traded |
| excute_price |  | no | Price per share |
| excute_date |  | no | YYYYMMDD |
| account_id |  | no | Settling account business ID |
| account_name |  | no | Settling account display name |
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
| stock_id | string | yes | FK to Stock_Journal.stock_id |
| excute_type | string | yes | buy / sell / dividend |
| excute_amount | number | yes | Quantity traded |
| excute_price | number | yes | Price per share |
| excute_date | string | yes | YYYYMMDD |
| account_id | string | yes | Settling account business ID |
| account_name | string | yes | Settling account display name |
| memo |  | no | Free-form memo |

Example:

```json
{
  "status": 1,
  "data": {
    "account_id": "BANK-CHASE-01",
    "account_name": "Chase Checking",
    "distinct_number": 1,
    "excute_amount": 10.0,
    "excute_date": "20260418",
    "excute_price": 180.5,
    "excute_type": "buy",
    "memo": "Initial buy",
    "stock_id": "STK-H-001"
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

### GET /assets/stocks/{stock_id}/details

**List stock transactions**

Return all buy/sell/stock-dividend/cash-dividend transactions for a holding.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| stock_id | path | string | yes |  |

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
| stock_id | string | yes | FK to Stock_Journal.stock_id |
| excute_type | string | yes | buy / sell / dividend |
| excute_amount | number | yes | Quantity traded |
| excute_price | number | yes | Price per share |
| excute_date | string | yes | YYYYMMDD |
| account_id | string | yes | Settling account business ID |
| account_name | string | yes | Settling account display name |
| memo |  | no | Free-form memo |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "account_id": "BANK-CHASE-01",
      "account_name": "Chase Checking",
      "distinct_number": 1,
      "excute_amount": 10.0,
      "excute_date": "20260418",
      "excute_price": 180.5,
      "excute_type": "buy",
      "memo": "Initial buy",
      "stock_id": "STK-H-001"
    }
  ],
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Stock not found | `{"status": 0, "error": "Stock 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### POST /assets/stocks/{stock_id}/details

**Record stock transaction**

Record a buy/sell/stock-dividend/cash-dividend transaction.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| stock_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| stock_id | string | yes | FK to Stock_Journal.stock_id |
| excute_type | string (enum: 'buy', 'sell', 'stock', 'cash') | yes | Transaction type: buy/sell/stock/cash |
| excute_amount | number | yes | Quantity traded |
| excute_price | number | yes | Price per share |
| excute_date | string | yes | YYYYMMDD |
| account_id | string | yes | Settling account business ID |
| account_name | string | yes | Settling account display name |
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
| stock_id | string | yes | FK to Stock_Journal.stock_id |
| excute_type | string | yes | buy / sell / dividend |
| excute_amount | number | yes | Quantity traded |
| excute_price | number | yes | Price per share |
| excute_date | string | yes | YYYYMMDD |
| account_id | string | yes | Settling account business ID |
| account_name | string | yes | Settling account display name |
| memo |  | no | Free-form memo |

Example:

```json
{
  "status": 1,
  "data": {
    "account_id": "BANK-CHASE-01",
    "account_name": "Chase Checking",
    "distinct_number": 1,
    "excute_amount": 10.0,
    "excute_date": "20260418",
    "excute_price": 180.5,
    "excute_type": "buy",
    "memo": "Initial buy",
    "stock_id": "STK-H-001"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Stock not found | `{"status": 0, "error": "Stock 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
