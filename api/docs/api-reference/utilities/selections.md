# Utilities — Selections

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### GET /utilities/selections/accounts

**List accounts grouped by type**

Return active accounts grouped by account_type, ordered by account_index ASC.

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
| label | string | yes | Group label (e.g. account type) |
| options | array<SelectionOption> | yes | Options that belong to this group |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "label": "BANK",
      "options": [
        {
          "label": "Cash — NTD",
          "value": "1"
        }
      ]
    }
  ],
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### GET /utilities/selections/codes

**List top-level codes grouped by code_type**

Return codes whose parent_id is NULL, grouped by code_type and ordered by code_index ASC.

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
| label | string | yes | Group label (e.g. account type) |
| options | array<SelectionOption> | yes | Options that belong to this group |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "label": "BANK",
      "options": [
        {
          "label": "Cash — NTD",
          "value": "1"
        }
      ]
    }
  ],
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### GET /utilities/selections/codes/{parent_id}

**List sub-codes for a parent code**

Return children of the parent code (parent_id) as a single 'sub' group.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| parent_id | path | string | yes | Parent code_id |

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
| label | string | yes | Group label (e.g. account type) |
| options | array<SelectionOption> | yes | Options that belong to this group |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "label": "BANK",
      "options": [
        {
          "label": "Cash — NTD",
          "value": "1"
        }
      ]
    }
  ],
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Parent code has no children | `{"status": 0, "error": "Parent code 'XYZ' has no children", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### GET /utilities/selections/credit-cards

**List credit cards as a single group**

Return active credit cards in one group labelled 'Credit_Card'.

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
| label | string | yes | Group label (e.g. account type) |
| options | array<SelectionOption> | yes | Options that belong to this group |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "label": "BANK",
      "options": [
        {
          "label": "Cash — NTD",
          "value": "1"
        }
      ]
    }
  ],
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### GET /utilities/selections/estates

**List estates as a single group**

Return active estates (estate_status != 'sold') in one group labelled 'Estate'.

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
| label | string | yes | Group label (e.g. account type) |
| options | array<SelectionOption> | yes | Options that belong to this group |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "label": "BANK",
      "options": [
        {
          "label": "Cash — NTD",
          "value": "1"
        }
      ]
    }
  ],
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### GET /utilities/selections/insurances

**List insurance policies as a single group**

Return open insurance policies (has_closed != 'Y') in one group labelled 'Insurance'.

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
| label | string | yes | Group label (e.g. account type) |
| options | array<SelectionOption> | yes | Options that belong to this group |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "label": "BANK",
      "options": [
        {
          "label": "Cash — NTD",
          "value": "1"
        }
      ]
    }
  ],
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### GET /utilities/selections/loans

**List loans as a single group**

Return loans in one group labelled 'Loan'.

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
| label | string | yes | Group label (e.g. account type) |
| options | array<SelectionOption> | yes | Options that belong to this group |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "label": "BANK",
      "options": [
        {
          "label": "Cash — NTD",
          "value": "1"
        }
      ]
    }
  ],
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### GET /utilities/selections/other-asset-types

**List distinct asset_type values from Other_Asset**

Return one group whose options are the distinct asset_type values across active Other_Asset rows. Drives the 'transfer to other asset' sub-category dropdown so it stays in sync with the user's asset setup.

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
| label | string | yes | Group label (e.g. account type) |
| options | array<SelectionOption> | yes | Options that belong to this group |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "label": "BANK",
      "options": [
        {
          "label": "Cash — NTD",
          "value": "1"
        }
      ]
    }
  ],
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### GET /utilities/selections/stock-categories

**List active stock categories as a single group**

Return active (in_use='Y') stock allocation categories in one group labelled 'Stock_Category', ordered by category_index. Drives the allocation-category dropdown on the stock holding form.

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
| label | string | yes | Group label (e.g. account type) |
| options | array<SelectionOption> | yes | Options that belong to this group |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "label": "BANK",
      "options": [
        {
          "label": "Cash — NTD",
          "value": "1"
        }
      ]
    }
  ],
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### GET /utilities/selections/stocks

**List stock holdings grouped by asset_id**

Return every Stock_Journal row grouped by its parent asset_id; each option's label is '<stock_code> <stock_name>' for filterable dropdowns.

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
| label | string | yes | Group label (e.g. account type) |
| options | array<SelectionOption> | yes | Options that belong to this group |

Example:

```json
{
  "status": 1,
  "data": [
    {
      "label": "BANK",
      "options": [
        {
          "label": "Cash — NTD",
          "value": "1"
        }
      ]
    }
  ],
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
