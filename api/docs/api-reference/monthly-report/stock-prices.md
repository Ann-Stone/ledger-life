# Monthly Report — Stock Prices

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### POST /monthly-report/stock-prices

**Insert a stock price record (optionally fetch yfinance)**

Persist a new StockPriceHistory row. When trigger_yfinance is True the close price is overwritten by yfinance.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| stock_code | string | yes | Ticker symbol |
| fetch_date | string | yes | YYYYMMDD |
| open_price | number | yes | Open price |
| highest_price | number | yes | Daily high |
| lowest_price | number | yes | Daily low |
| close_price | number | yes | Close price (overwritten when trigger_yfinance is True) |
| trigger_yfinance | boolean | no | When True, fetch close price from yfinance and overwrite close_price. |

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
| stock_code | string | yes | Ticker symbol |
| fetch_date | string | yes | YYYYMMDD |
| open_price | number | yes | Open price |
| highest_price | number | yes | Daily high |
| lowest_price | number | yes | Daily low |
| close_price | number | yes | Close price |

Example:

```json
{
  "status": 1,
  "data": {
    "close_price": 181.8,
    "fetch_date": "20260418",
    "highest_price": 182.5,
    "lowest_price": 179.2,
    "open_price": 180.0,
    "stock_code": "AAPL"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
| 502 | yfinance fetch failed | `{"status": 0, "error": "yfinance fetch failed", "msg": "fail"}` |

### GET /monthly-report/stock-prices/{vesting_month}

**Month-level closing prices for held stocks**

For every stock present in the holdings table, return the most recent StockPriceHistory close on or before month-end (falling back to the latest prior row when the month has none).

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| vesting_month | path | string | yes | YYYYMM |

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
| stock_code | string | yes | Ticker symbol |
| stock_name | string | yes | Stock display name |
| close_price |  | no | Close price of the most recent in-month row, or null when the requested month has no price data (signals a fetch is needed). |
| fetch_date |  | no | YYYYMMDD of the row the close_price came from, or null when the month has no price data. |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "close_price": 181.8,
      "fetch_date": "20260430",
      "stock_code": "AAPL",
      "stock_name": "Apple Inc."
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
