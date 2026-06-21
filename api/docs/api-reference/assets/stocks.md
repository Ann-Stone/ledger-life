# Assets — Stocks

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /assets/stocks

**List stock holdings**

Return stock holdings filtered by asset_id.

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
| stock_id | string | yes | Holding business ID |
| stock_code | string | yes | Ticker symbol |
| stock_name | string | yes | Stock display name |
| asset_id | string | yes | Asset category ID |
| expected_spend | number | yes | Planned investment amount for this holding entry (one-shot purchase budget; not a recurring premium — see Insurance.expected_spend for that) |
| category_id |  | no | Allocation category id (references Stock_Category.category_id); null = unclassified |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "asset_id": "AC-STK-001",
      "category_id": "SC-001",
      "expected_spend": 10000.0,
      "stock_code": "AAPL",
      "stock_id": "STK-H-001",
      "stock_name": "Apple Inc."
    }
  ],
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 400 | Invalid query | `{"status": 0, "error": "Invalid query", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### POST /assets/stocks

**Create stock holding**

Create a new stock holding under an asset category.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| stock_id | string | yes | Holding business ID |
| stock_code | string | yes | Ticker symbol |
| stock_name | string | yes | Stock display name |
| asset_id | string | yes | Asset category ID |
| expected_spend | number | yes | Planned investment amount for this holding entry (one-shot purchase budget; not a recurring premium — see Insurance.expected_spend for that) |
| category_id |  | no | Allocation category id (references Stock_Category.category_id); optional at creation |

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
| stock_id | string | yes | Holding business ID |
| stock_code | string | yes | Ticker symbol |
| stock_name | string | yes | Stock display name |
| asset_id | string | yes | Asset category ID |
| expected_spend | number | yes | Planned investment amount for this holding entry (one-shot purchase budget; not a recurring premium — see Insurance.expected_spend for that) |
| category_id |  | no | Allocation category id (references Stock_Category.category_id); null = unclassified |

Example:

```json
{
  "status": 1,
  "data": {
    "asset_id": "AC-STK-001",
    "category_id": "SC-001",
    "expected_spend": 10000.0,
    "stock_code": "AAPL",
    "stock_id": "STK-H-001",
    "stock_name": "Apple Inc."
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 409 | Duplicate stock_id | `{"status": 0, "error": "Duplicate stock_id", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### GET /assets/stocks/summary

**Per-stock P&L summary**

Computed per-holding performance for an asset category: moving-average cost, latest market value, realized gain (capital gains, dividends excluded), cumulative dividends, unrealized gain/%, and trailing-12m cash yield / cost yield. Figures are in each holding's own currency. Derived fresh from Stock_Detail (the only per-stock source).

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| asset_id | query | string | yes | Parent asset category id |
| as_of_month | query |  | no | Valuation month as YYYYMM; defaults to the current month. |

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
| stock_id | string | yes | Holding business ID |
| stock_code | string | yes | Ticker symbol |
| stock_name | string | yes | Stock display name |
| shares | number | yes | Net shares currently held |
| cost | number | yes | Moving-average cost basis of held shares (own currency) |
| market_value |  | no | shares × latest close price; null when no price snapshot exists |
| realized | number | yes | Signed realized capital gain/loss from sells (own currency); dividends excluded |
| dividends_total | number | yes | Cumulative cash dividends received (own currency) |
| unrealized |  | no | market_value − cost; null when no price snapshot exists |
| unrealized_pct |  | no | unrealized ÷ cost as a fraction; null when cost is 0 or no price |
| cash_yield |  | no | Trailing-12-month cash dividends ÷ market_value (fraction); null when market_value is 0/None |
| cost_yield |  | no | Cumulative cash dividends ÷ cost (fraction); null when cost is 0 |
| fx_code | string | yes | Currency the figures are expressed in |
| close_price |  | no | Latest close price used for market_value; null when none exists |
| price_date |  | no | YYYYMMDD of the close price used; null when none exists |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "cash_yield": 0.0278,
      "close_price": 180.0,
      "cost": 14850.0,
      "cost_yield": 0.0303,
      "dividends_total": 450.0,
      "fx_code": "USD",
      "market_value": 16200.0,
      "price_date": "20260430",
      "realized": 1500.0,
      "shares": 90.0,
      "stock_code": "AAPL",
      "stock_id": "STK-H-001",
      "stock_name": "Apple Inc.",
      "unrealized": 1350.0,
      "unrealized_pct": 0.0909
    }
  ],
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 400 | Invalid query | `{"status": 0, "error": "Invalid query", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### DELETE /assets/stocks/{stock_id}

**Delete stock holding**

Delete a stock holding by id.

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
| 404 | Stock not found | `{"status": 0, "error": "Stock 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### PUT /assets/stocks/{stock_id}

**Update stock holding**

Update a stock holding by id; any omitted field is left unchanged.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| stock_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| stock_code |  | no | Ticker symbol |
| stock_name |  | no | Stock display name |
| asset_id |  | no | Asset category ID |
| expected_spend |  | no | Planned investment amount for this holding entry (one-shot purchase budget; not a recurring premium — see Insurance.expected_spend for that) |
| category_id |  | no | Allocation category id (references Stock_Category.category_id) |

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
| stock_id | string | yes | Holding business ID |
| stock_code | string | yes | Ticker symbol |
| stock_name | string | yes | Stock display name |
| asset_id | string | yes | Asset category ID |
| expected_spend | number | yes | Planned investment amount for this holding entry (one-shot purchase budget; not a recurring premium — see Insurance.expected_spend for that) |
| category_id |  | no | Allocation category id (references Stock_Category.category_id); null = unclassified |

Example:

```json
{
  "status": 1,
  "data": {
    "asset_id": "AC-STK-001",
    "category_id": "SC-001",
    "expected_spend": 10000.0,
    "stock_code": "AAPL",
    "stock_id": "STK-H-001",
    "stock_name": "Apple Inc."
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
