# Monthly Report — Journals Analytics

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /monthly-report/journals/{vesting_month}/expenditure-budget

**Actual vs budget per category**

Compare expected (Budget.expected<MM>) vs actual (Journal.spending sum) per category, returning diff and usage_rate.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| vesting_month | path | string | yes |  |

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
| rows | array<ExpenditureBudgetRow> | yes | Per action_main_type comparison rows |

Example:

```json
{
  "status": 1,
  "data": {
    "rows": [
      {
        "action_main_type": "expense",
        "actual": 28500.5,
        "diff": -1499.5,
        "expected": 30000.0,
        "usage_rate": 0.95
      }
    ]
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | No data for the month | `{"status": 0, "error": "No data for the month", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### GET /monthly-report/journals/{vesting_month}/expenditure-ratio

**Monthly expenditure ratio (inner/outer pie)**

Return outer/inner aggregations of journal spending for the given month. Outer = grouped by action_main_type; inner = grouped by action_sub_type. Excludes 'invest' and 'transfer' main types.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| vesting_month | path | string | yes |  |

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
| outer | array<ExpenditureRatioItem> | yes | Outer pie: amounts grouped by action_main_type |
| inner | array<ExpenditureRatioItem> | yes | Inner pie: amounts grouped by action_sub_type |

Example:

```json
{
  "status": 1,
  "data": {
    "inner": [
      {
        "name": "expense",
        "value": 1234.56
      }
    ],
    "outer": [
      {
        "name": "expense",
        "value": 1234.56
      }
    ]
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | No data for the month | `{"status": 0, "error": "No data for the month", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### GET /monthly-report/journals/{vesting_month}/invest-ratio

**Monthly invest ratio**

Aggregate journal spending whose action_main_type == 'invest', grouped by action_sub_type.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| vesting_month | path | string | yes |  |

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
| items | array<InvestRatioItem> | yes | Per-subtype invest amounts |

Example:

```json
{
  "status": 1,
  "data": {
    "items": [
      {
        "name": "stock",
        "value": 5000.0
      }
    ]
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | No data for the month | `{"status": 0, "error": "No data for the month", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### GET /monthly-report/journals/{vesting_month}/liability

**Credit-card liability breakdown**

Aggregate journal spending whose spend_way_type == 'credit_card', grouped by credit card.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| vesting_month | path | string | yes |  |

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
| items | array<LiabilityItem> | yes | Per-card credit card liability for the month |

Example:

```json
{
  "status": 1,
  "data": {
    "items": [
      {
        "amount": 2500.0,
        "credit_card_id": "CC-VISA-01",
        "credit_card_name": "Chase Sapphire"
      }
    ]
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | No data for the month | `{"status": 0, "error": "No data for the month", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
