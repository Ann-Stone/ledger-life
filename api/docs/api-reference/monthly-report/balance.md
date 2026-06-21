# Monthly Report — Balance

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### PUT /monthly-report/balance/{vesting_month}/settle

**Run monthly balance settlement**

Snapshot every asset/liability net value for the vesting month. Idempotent: per-asset-type tables are delete+reinsert; AccountBalance and CreditCardBalance use cascade-delete from the target month forward to invalidate later carry-forward snapshots.

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

data:

| name | type | required | description |
| --- | --- | --- | --- |
| vesting_month | string | yes | Settled vesting month (YYYYMM) |
| estate_rows | integer | yes | Estate snapshot rows inserted |
| insurance_rows | integer | yes | Insurance snapshot rows inserted |
| loan_rows | integer | yes | Loan snapshot rows inserted |
| stock_rows | integer | yes | Stock snapshot rows inserted (skips zero-amount holdings) |
| account_rows | integer | yes | AccountBalance rows recomputed for the month |
| credit_card_rows | integer | yes | CreditCardBalance rows recomputed for the month |

Example:

```json
{
  "status": 1,
  "data": {
    "account_rows": 4,
    "credit_card_rows": 2,
    "estate_rows": 1,
    "insurance_rows": 1,
    "loan_rows": 1,
    "stock_rows": 2,
    "vesting_month": "202604"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Vesting month has no eligible data | `{"status": 0, "error": "Vesting month has no eligible data", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
