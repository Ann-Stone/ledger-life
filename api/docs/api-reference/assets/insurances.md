# Assets — Insurances

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /assets/insurances

**List insurance policies**

Return policies under a given asset_id.

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
| insurance_id | string | yes | Policy business ID |
| insurance_name | string | yes | Policy display name |
| asset_id | string | yes | Asset category ID |
| in_account | string | yes | Paying account id |
| out_account | string | yes | Disbursing account id |
| start_date | string | yes | YYYYMMDD |
| end_date | string | yes | YYYYMMDD |
| pay_type | string | yes | Premium cadence |
| pay_day | string | yes | Premium date(s); 'DD' / 'MM/DD' / 'MM/DD,...' by pay_type |
| expected_spend | number | yes | Expected premium per pay_type cadence (e.g. annual premium amount when pay_type='annual') |
| has_closed | string | yes | Closed flag |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "asset_id": "AC-INS-001",
      "end_date": "20500101",
      "expected_spend": 1200.0,
      "has_closed": "N",
      "in_account": "BANK-CHASE-01",
      "insurance_id": "INS-001",
      "insurance_name": "Whole life policy",
      "out_account": "BANK-CHASE-01",
      "pay_day": "01/15",
      "pay_type": "annual",
      "start_date": "20200101"
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

### POST /assets/insurances

**Create insurance policy**

Create a policy; start/end dates accept ISO 8601 and are stored as YYYYMMDD.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| insurance_id | string | yes | Policy business ID |
| insurance_name | string | yes | Policy display name |
| asset_id | string | yes | Asset category ID |
| in_account | string | yes | Paying account id |
| out_account | string | yes | Disbursing account id |
| start_date | string | yes | YYYYMMDD |
| end_date | string | yes | YYYYMMDD |
| pay_type | string | yes | Premium cadence |
| pay_day | string | yes | Premium date(s); 'DD' / 'MM/DD' / 'MM/DD,...' by pay_type |
| expected_spend | number | yes | Expected premium per pay_type cadence (e.g. annual premium amount when pay_type='annual') |
| has_closed | string (enum: 'Y', 'N') | yes | Closed flag (Y/N) |

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
| insurance_id | string | yes | Policy business ID |
| insurance_name | string | yes | Policy display name |
| asset_id | string | yes | Asset category ID |
| in_account | string | yes | Paying account id |
| out_account | string | yes | Disbursing account id |
| start_date | string | yes | YYYYMMDD |
| end_date | string | yes | YYYYMMDD |
| pay_type | string | yes | Premium cadence |
| pay_day | string | yes | Premium date(s); 'DD' / 'MM/DD' / 'MM/DD,...' by pay_type |
| expected_spend | number | yes | Expected premium per pay_type cadence (e.g. annual premium amount when pay_type='annual') |
| has_closed | string | yes | Closed flag |

Example:

```json
{
  "status": 1,
  "data": {
    "asset_id": "AC-INS-001",
    "end_date": "20500101",
    "expected_spend": 1200.0,
    "has_closed": "N",
    "in_account": "BANK-CHASE-01",
    "insurance_id": "INS-001",
    "insurance_name": "Whole life policy",
    "out_account": "BANK-CHASE-01",
    "pay_day": "01/15",
    "pay_type": "annual",
    "start_date": "20200101"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 409 | Duplicate insurance_id | `{"status": 0, "error": "Duplicate insurance_id", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### DELETE /assets/insurances/{insurance_id}

**Delete insurance policy**

Delete a policy by id.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| insurance_id | path | string | yes |  |

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
| 404 | Insurance not found | `{"status": 0, "error": "Insurance 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### PUT /assets/insurances/{insurance_id}

**Update insurance policy**

Update a policy by id; any omitted field is left unchanged.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| insurance_id | path | string | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| insurance_name |  | no | Policy display name |
| asset_id |  | no | Asset category ID |
| in_account |  | no | Paying account id |
| out_account |  | no | Disbursing account id |
| start_date |  | no | YYYYMMDD |
| end_date |  | no | YYYYMMDD |
| pay_type |  | no | Premium cadence |
| pay_day |  | no | Premium date(s); 'DD' / 'MM/DD' / 'MM/DD,...' by pay_type |
| expected_spend |  | no | Expected premium per pay_type cadence (e.g. annual premium amount when pay_type='annual') |
| has_closed |  | no | Closed flag |

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
| insurance_id | string | yes | Policy business ID |
| insurance_name | string | yes | Policy display name |
| asset_id | string | yes | Asset category ID |
| in_account | string | yes | Paying account id |
| out_account | string | yes | Disbursing account id |
| start_date | string | yes | YYYYMMDD |
| end_date | string | yes | YYYYMMDD |
| pay_type | string | yes | Premium cadence |
| pay_day | string | yes | Premium date(s); 'DD' / 'MM/DD' / 'MM/DD,...' by pay_type |
| expected_spend | number | yes | Expected premium per pay_type cadence (e.g. annual premium amount when pay_type='annual') |
| has_closed | string | yes | Closed flag |

Example:

```json
{
  "status": 1,
  "data": {
    "asset_id": "AC-INS-001",
    "end_date": "20500101",
    "expected_spend": 1200.0,
    "has_closed": "N",
    "in_account": "BANK-CHASE-01",
    "insurance_id": "INS-001",
    "insurance_name": "Whole life policy",
    "out_account": "BANK-CHASE-01",
    "pay_day": "01/15",
    "pay_type": "annual",
    "start_date": "20200101"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Insurance not found | `{"status": 0, "error": "Insurance 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
