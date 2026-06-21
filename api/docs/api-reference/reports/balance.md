# Reports — Balance

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /reports/balance

**Get current balance sheet**

Aggregates latest snapshots per asset/liability entity, FX-converts to base currency, returns net worth.

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
| assets | BalanceAssets | yes | Asset breakdown |
| liabilities | BalanceLiabilities | yes | Liability breakdown |
| net_worth | number | yes | Total assets minus total liabilities in base currency |

Example:

```json
{
  "status": 1,
  "data": {
    "assets": {
      "accounts": [
        {
          "amount": 123456.78,
          "currency": "TWD",
          "name": "Cathay Bank",
          "original_amount": 123456.78
        }
      ],
      "estates": [],
      "insurances": [],
      "stocks": []
    },
    "liabilities": {
      "credit_cards": [],
      "loans": [
        {
          "amount": -250000.0,
          "currency": "TWD",
          "name": "Mortgage",
          "original_amount": -250000.0
        }
      ]
    },
    "net_worth": 987654.32
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
