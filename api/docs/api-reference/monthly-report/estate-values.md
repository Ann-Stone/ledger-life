# Monthly Report — Estate Values

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### POST /monthly-report/estate-values

**Record (insert or update) a property's market value for a month**

Upsert the 估值 for an (estate, month). Idempotent on the composite key; 404 when the estate does not exist.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| estate_id | string | yes | FK to Estate.estate_id |
| vesting_month | string | yes | YYYYMM the value is effective from |
| market_value | number | yes | Appraised market value in estate currency |
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
| estate_id | string | yes | FK to Estate.estate_id |
| vesting_month | string | yes | YYYYMM the value is effective from |
| market_value | number | yes | Appraised market value in estate currency |
| memo |  | no | Free-form memo |

Example:

```json
{
  "status": 1,
  "data": {
    "estate_id": "EST-001",
    "market_value": 13800000.0,
    "memo": "同社區 2026Q1 實價登錄估算",
    "vesting_month": "202604"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Estate not found | `{"status": 0, "error": "Estate 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### POST /monthly-report/estate-values/refresh-index

**Refresh the house-price index from data.gov.tw (best-effort)**

Pull the latest 住宅價格指數 (repeat-sales, market-based) from data.gov.tw open data and upsert the quarterly series. Best-effort: on a fetch/parse failure it keeps the existing data and returns ok=false.

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
| region | string | yes | Region refreshed |
| upserted | integer | yes | Number of quarters inserted/updated |
| ok | boolean | yes | False when the fetch failed and existing data was kept |

Example:

```json
{
  "status": 1,
  "data": {
    "ok": true,
    "region": "臺北市全市",
    "upserted": 48
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### GET /monthly-report/estate-values/{vesting_month}

**Month-level market values for every property**

For every real-estate holding, return the latest recorded market value (估值) on or before month-end (carried forward), with a ``recorded`` flag that is true only when entered in this exact month.

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
| estate_id | string | yes | Estate business ID |
| estate_name | string | yes | Estate display name |
| market_value |  | no | Latest recorded market value on or before the month, or null when none |
| vesting_month |  | no | YYYYMM the market_value was recorded for, or null when none |
| recorded | boolean | no | True when a value was recorded in this exact month (not carried forward) |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "estate_id": "EST-001",
      "estate_name": "主要住所",
      "market_value": 13800000.0,
      "recorded": true,
      "vesting_month": "202604"
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

### GET /monthly-report/estate-values/{vesting_month}/suggestions

**Index-based suggested market value per property**

For each estate, suggest a market value = acquisition cost × (current index / obtain-quarter index), using the configured house-price index region. suggested_market_value is null when the index is unavailable. The suggestion is advisory — a recorded value always overrides it.

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
| estate_id | string | yes | Estate business ID |
| estate_name | string | yes | Estate display name |
| cost | number | yes | Acquisition cost (sum of estate journals) |
| suggested_market_value |  | no | cost × (current index / obtain-quarter index); null when the index is unavailable |
| region | string | yes | Index region used for the suggestion |
| obtain_quarter |  | no | Quarter of the estate's obtain_date |
| current_quarter |  | no | Latest index quarter at or before the report month |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "cost": 10000000.0,
      "current_quarter": "2024Q1",
      "estate_id": "EST-001",
      "estate_name": "主要住所",
      "obtain_quarter": "2020Q1",
      "region": "臺北市全市",
      "suggested_market_value": 13773000.0
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
