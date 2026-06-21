# Settings — Budgets

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### PUT /settings/budgets

**Bulk update budgets**

Update multiple Budget rows in one call. Each item is matched by (budget_year, category_code). Transactional — if any row is missing, all updates are rolled back.

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
| budget_year | string | yes | YYYY |
| category_code | string | yes | FK to CodeData.code_id |
| category_name | string | yes | Category display name |
| code_type | string | yes | Code type |
| expected01 | number | yes | Month 01 expected |
| expected02 | number | yes | Month 02 expected |
| expected03 | number | yes | Month 03 expected |
| expected04 | number | yes | Month 04 expected |
| expected05 | number | yes | Month 05 expected |
| expected06 | number | yes | Month 06 expected |
| expected07 | number | yes | Month 07 expected |
| expected08 | number | yes | Month 08 expected |
| expected09 | number | yes | Month 09 expected |
| expected10 | number | yes | Month 10 expected |
| expected11 | number | yes | Month 11 expected |
| expected12 | number | yes | Month 12 expected |
| annual_amount |  | no | Annual envelope for annual-event categories |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "budget_year": "2026",
      "category_code": "INC01",
      "category_name": "Salary",
      "code_type": "income",
      "expected01": 100000.0,
      "expected02": 100000.0,
      "expected03": 100000.0,
      "expected04": 100000.0,
      "expected05": 100000.0,
      "expected06": 100000.0,
      "expected07": 100000.0,
      "expected08": 100000.0,
      "expected09": 100000.0,
      "expected10": 100000.0,
      "expected11": 100000.0,
      "expected12": 200000.0
    }
  ],
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Budget rows not found | `{"status": 0, "error": "Budget rows 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### GET /settings/budgets/year-range

**Available budget years**

Return distinct budget_year values present in Budget, ascending.

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
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### GET /settings/budgets/{year}

**Budgets for a year**

Return all Budget rows for the given year ordered by category_code.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| year | path | integer | yes |  |

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
| budget_year | string | yes | YYYY |
| category_code | string | yes | FK to CodeData.code_id |
| category_name | string | yes | Category display name |
| code_type | string | yes | Code type |
| expected01 | number | yes | Month 01 expected |
| expected02 | number | yes | Month 02 expected |
| expected03 | number | yes | Month 03 expected |
| expected04 | number | yes | Month 04 expected |
| expected05 | number | yes | Month 05 expected |
| expected06 | number | yes | Month 06 expected |
| expected07 | number | yes | Month 07 expected |
| expected08 | number | yes | Month 08 expected |
| expected09 | number | yes | Month 09 expected |
| expected10 | number | yes | Month 10 expected |
| expected11 | number | yes | Month 11 expected |
| expected12 | number | yes | Month 12 expected |
| annual_amount |  | no | Annual envelope for annual-event categories |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "budget_year": "2026",
      "category_code": "INC01",
      "category_name": "Salary",
      "code_type": "income",
      "expected01": 100000.0,
      "expected02": 100000.0,
      "expected03": 100000.0,
      "expected04": 100000.0,
      "expected05": 100000.0,
      "expected06": 100000.0,
      "expected07": 100000.0,
      "expected08": 100000.0,
      "expected09": 100000.0,
      "expected10": 100000.0,
      "expected11": 100000.0,
      "expected12": 200000.0
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

### POST /settings/budgets/{year}/apply

**Apply (upsert) budget rows**

Upsert the provided budget rows, inserting rows that do not exist yet. Use this to persist a (possibly edited) suggestion for a brand-new year.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| year | path | integer | yes |  |

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
| budget_year | string | yes | YYYY |
| category_code | string | yes | FK to CodeData.code_id |
| category_name | string | yes | Category display name |
| code_type | string | yes | Code type |
| expected01 | number | yes | Month 01 expected |
| expected02 | number | yes | Month 02 expected |
| expected03 | number | yes | Month 03 expected |
| expected04 | number | yes | Month 04 expected |
| expected05 | number | yes | Month 05 expected |
| expected06 | number | yes | Month 06 expected |
| expected07 | number | yes | Month 07 expected |
| expected08 | number | yes | Month 08 expected |
| expected09 | number | yes | Month 09 expected |
| expected10 | number | yes | Month 10 expected |
| expected11 | number | yes | Month 11 expected |
| expected12 | number | yes | Month 12 expected |
| annual_amount |  | no | Annual envelope for annual-event categories |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "budget_year": "2026",
      "category_code": "INC01",
      "category_name": "Salary",
      "code_type": "income",
      "expected01": 100000.0,
      "expected02": 100000.0,
      "expected03": 100000.0,
      "expected04": 100000.0,
      "expected05": 100000.0,
      "expected06": 100000.0,
      "expected07": 100000.0,
      "expected08": 100000.0,
      "expected09": 100000.0,
      "expected10": 100000.0,
      "expected11": 100000.0,
      "expected12": 200000.0
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

### POST /settings/budgets/{year}/suggest

**Suggest budget from recent years**

Compute a suggested budget for {year} from the last up-to-3 years of Journal spending: per-calendar-month median for ordinary Fixed/Floating categories, and a single annual-total median envelope (annual_amount) for categories flagged is_annual_event. Returns the suggestion WITHOUT persisting so the client can preview and edit before applying.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| year | path | integer | yes |  |

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
| budget_year | string | yes | YYYY |
| category_code | string | yes | FK to CodeData.code_id |
| category_name | string | yes | Category display name |
| code_type | string | yes | Code type |
| expected01 | number | yes | Month 01 expected |
| expected02 | number | yes | Month 02 expected |
| expected03 | number | yes | Month 03 expected |
| expected04 | number | yes | Month 04 expected |
| expected05 | number | yes | Month 05 expected |
| expected06 | number | yes | Month 06 expected |
| expected07 | number | yes | Month 07 expected |
| expected08 | number | yes | Month 08 expected |
| expected09 | number | yes | Month 09 expected |
| expected10 | number | yes | Month 10 expected |
| expected11 | number | yes | Month 11 expected |
| expected12 | number | yes | Month 12 expected |
| annual_amount |  | no | Annual envelope for annual-event categories |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "budget_year": "2026",
      "category_code": "INC01",
      "category_name": "Salary",
      "code_type": "income",
      "expected01": 100000.0,
      "expected02": 100000.0,
      "expected03": 100000.0,
      "expected04": 100000.0,
      "expected05": 100000.0,
      "expected06": 100000.0,
      "expected07": 100000.0,
      "expected08": 100000.0,
      "expected09": 100000.0,
      "expected10": 100000.0,
      "expected11": 100000.0,
      "expected12": 200000.0
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
