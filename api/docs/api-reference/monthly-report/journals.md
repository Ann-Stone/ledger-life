# Monthly Report — Journals

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

### Polymorphic references

Journal rows carry two polymorphic foreign keys. Frontend forms must keep the
discriminator and the table consistent or the row will fail validation on the
server. The full matrix is:

| field group | type value | table value | id value points to | source endpoint |
| --- | --- | --- | --- | --- |
| `spend_way_*` | `account` | `Account` | `Account.id` (PK) | `GET /utilities/selections/accounts` |
| `spend_way_*` | `credit_card` | `Credit_Card` | `CreditCard.credit_card_id` | `GET /utilities/selections/credit-cards` |
| `action_main_*` | `Fixed` / `Floating` / `Income` / `Invest` / `Transfer` (user-configurable, mirrors `Code_Data.code_type`) | `Code_Data` | `Code_Data.code_id` (where `parent_id IS NULL`) | `GET /utilities/selections/codes` |
| `action_sub_*` | mirror of the sub-code's `Code_Data.code_type`, or `null` | `Code_Data` or `null` | `Code_Data.code_id` whose `parent_id == action_main`, or `null` | `GET /utilities/selections/codes/{action_main}` |

Hard rules the API enforces:

- `spend_way_table` must match the `spend_way_type` mapping above; mismatched values cause a 422.
- All three `action_sub_*` fields are populated together, or all three are `null`. Partial population is rejected.
- `action_main_table` is always `"Code_Data"` for journal entries created by the UI; legacy importers may emit other table names but new writes must use `Code_Data`.

## Endpoints

### POST /monthly-report/journals

**Create a journal entry**

Persist a new Journal row. distinct_number is auto-assigned.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| vesting_month | string | yes | YYYYMM |
| spend_date | string | yes | YYYYMMDD |
| spend_way | string | yes | Payment source id |
| spend_way_type | string | yes | Polymorphic discriminator for spend_way. Valid values: 'account' (spend_way_table='Account', spend_way → Account.id PK) | 'credit_card' (spend_way_table='Credit_Card', spend_way → CreditCard.credit_card_id PK). |
| spend_way_table | string | yes | Source SQL table for spend_way. Must be 'Account' when spend_way_type='account', or 'Credit_Card' when spend_way_type='credit_card'. |
| action_main | string | yes | Reference to a Code_Data row's code_id. The set of valid code_ids is user-configurable via Settings → Codes. |
| action_main_type | string | yes | Mirror of the referenced Code_Data.code_type. Common values: 'Fixed', 'Floating', 'Income', 'Invest', 'Transfer'. Frontend should fetch /utilities/selections/codes for the live set. |
| action_main_table | string | yes | Source SQL table for action_main. Always 'Code_Data' for code-driven classification. |
| action_sub |  | no | Optional sub-classification: a Code_Data.code_id whose parent_id equals action_main. Null when there is no secondary breakdown. |
| action_sub_type |  | no | Mirror of the sub-code's Code_Data.code_type. Null when action_sub is null. Either all three action_sub_* fields are populated together or all three are null. |
| action_sub_table |  | no | Source SQL table for action_sub. 'Code_Data' when action_sub is set, null otherwise. |
| spending | number | yes | Positive = income, negative = expense |
| invoice_number |  | no | Invoice number |
| note |  | no | Free-form note |

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
| vesting_month | string | yes | YYYYMM |
| spend_date | string | yes | YYYYMMDD |
| spend_way | string | yes | Payment source id |
| spend_way_type | string | yes | Polymorphic discriminator for spend_way. Valid values: 'account' (spend_way_table='Account', spend_way → Account.id PK) | 'credit_card' (spend_way_table='Credit_Card', spend_way → CreditCard.credit_card_id PK). |
| spend_way_table | string | yes | Source SQL table for spend_way. Must be 'Account' when spend_way_type='account', or 'Credit_Card' when spend_way_type='credit_card'. |
| action_main | string | yes | Reference to a Code_Data row's code_id. The set of valid code_ids is user-configurable via Settings → Codes. |
| action_main_type | string | yes | Mirror of the referenced Code_Data.code_type. Common values: 'Fixed', 'Floating', 'Income', 'Invest', 'Transfer'. Frontend should fetch /utilities/selections/codes for the live set. |
| action_main_table | string | yes | Source SQL table for action_main. Always 'Code_Data' for code-driven classification. |
| action_sub |  | no | Optional sub-classification: a Code_Data.code_id whose parent_id equals action_main. Null when there is no secondary breakdown. |
| action_sub_type |  | no | Mirror of the sub-code's Code_Data.code_type. Null when action_sub is null. Either all three action_sub_* fields are populated together or all three are null. |
| action_sub_table |  | no | Source SQL table for action_sub. 'Code_Data' when action_sub is set, null otherwise. |
| spending | number | yes | Signed amount |
| invoice_number |  | no | Invoice number |
| note |  | no | Free-form note |

Example:

```json
{
  "status": 1,
  "data": {
    "action_main": "EXP01",
    "action_main_table": "Code_Data",
    "action_main_type": "expense",
    "distinct_number": 1,
    "note": "Lunch",
    "spend_date": "20260418",
    "spend_way": "1",
    "spend_way_table": "Account",
    "spend_way_type": "account",
    "spending": -123.45,
    "vesting_month": "202604"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### GET /monthly-report/journals/uncategorized-summary

**Count uncategorized journals across all months**

Return the total number of Journal rows whose action_main_type falls outside every report bucket (expense/income/invest/transfer — e.g. legacy 'undefined'/'No'/'' values), plus a per-month breakdown ordered newest first. Months with zero uncategorized rows are omitted.

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
| total | integer | yes | Uncategorized journal rows across all months (action_main_type outside every report bucket) |
| months | array<UncategorizedMonthCount> | yes | Per-month breakdown, newest month first; months with zero rows omitted |

Example:

```json
{
  "status": 1,
  "data": {
    "months": [
      {
        "count": 87,
        "vesting_month": "202405"
      }
    ],
    "total": 2330
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### DELETE /monthly-report/journals/{journal_id}

**Delete a journal entry**

Delete a Journal identified by distinct_number.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| journal_id | path | integer | yes |  |

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
| 404 | Journal not found | `{"status": 0, "error": "Journal 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### PUT /monthly-report/journals/{journal_id}

**Update a journal entry**

Partial update of a Journal identified by distinct_number.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| journal_id | path | integer | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| vesting_month |  | no | YYYYMM |
| spend_date |  | no | YYYYMMDD |
| spend_way |  | no | Payment source id |
| spend_way_type |  | no | Polymorphic discriminator for spend_way. Valid values: 'account' (spend_way_table='Account', spend_way → Account.id PK) | 'credit_card' (spend_way_table='Credit_Card', spend_way → CreditCard.credit_card_id PK). |
| spend_way_table |  | no | Source SQL table for spend_way. Must be 'Account' when spend_way_type='account', or 'Credit_Card' when spend_way_type='credit_card'. |
| action_main |  | no | Reference to a Code_Data row's code_id. The set of valid code_ids is user-configurable via Settings → Codes. |
| action_main_type |  | no | Mirror of the referenced Code_Data.code_type. Common values: 'Fixed', 'Floating', 'Income', 'Invest', 'Transfer'. Frontend should fetch /utilities/selections/codes for the live set. |
| action_main_table |  | no | Source SQL table for action_main. Always 'Code_Data' for code-driven classification. |
| action_sub |  | no | Optional sub-classification: a Code_Data.code_id whose parent_id equals action_main. Null when there is no secondary breakdown. |
| action_sub_type |  | no | Mirror of the sub-code's Code_Data.code_type. Null when action_sub is null. Either all three action_sub_* fields are populated together or all three are null. |
| action_sub_table |  | no | Source SQL table for action_sub. 'Code_Data' when action_sub is set, null otherwise. |
| spending |  | no | Signed amount |
| invoice_number |  | no | Invoice number |
| note |  | no | Free-form note |

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
| vesting_month | string | yes | YYYYMM |
| spend_date | string | yes | YYYYMMDD |
| spend_way | string | yes | Payment source id |
| spend_way_type | string | yes | Polymorphic discriminator for spend_way. Valid values: 'account' (spend_way_table='Account', spend_way → Account.id PK) | 'credit_card' (spend_way_table='Credit_Card', spend_way → CreditCard.credit_card_id PK). |
| spend_way_table | string | yes | Source SQL table for spend_way. Must be 'Account' when spend_way_type='account', or 'Credit_Card' when spend_way_type='credit_card'. |
| action_main | string | yes | Reference to a Code_Data row's code_id. The set of valid code_ids is user-configurable via Settings → Codes. |
| action_main_type | string | yes | Mirror of the referenced Code_Data.code_type. Common values: 'Fixed', 'Floating', 'Income', 'Invest', 'Transfer'. Frontend should fetch /utilities/selections/codes for the live set. |
| action_main_table | string | yes | Source SQL table for action_main. Always 'Code_Data' for code-driven classification. |
| action_sub |  | no | Optional sub-classification: a Code_Data.code_id whose parent_id equals action_main. Null when there is no secondary breakdown. |
| action_sub_type |  | no | Mirror of the sub-code's Code_Data.code_type. Null when action_sub is null. Either all three action_sub_* fields are populated together or all three are null. |
| action_sub_table |  | no | Source SQL table for action_sub. 'Code_Data' when action_sub is set, null otherwise. |
| spending | number | yes | Signed amount |
| invoice_number |  | no | Invoice number |
| note |  | no | Free-form note |

Example:

```json
{
  "status": 1,
  "data": {
    "action_main": "EXP01",
    "action_main_table": "Code_Data",
    "action_main_type": "expense",
    "distinct_number": 1,
    "note": "Lunch",
    "spend_date": "20260418",
    "spend_way": "1",
    "spend_way_table": "Account",
    "spend_way_type": "account",
    "spending": -123.45,
    "vesting_month": "202604"
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Journal not found | `{"status": 0, "error": "Journal 42 not found", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### GET /monthly-report/journals/{vesting_month}

**List journals for a month with gain/loss**

Return all Journal entries whose vesting_month matches the path parameter, ordered by spend_date. The response also includes the FX-converted gain/loss total for the month.

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
| items | array<JournalRead> | yes | Journal entries for the month, ordered by spend_date |
| gain_loss | number | yes | Net gain/loss for the month after FX conversion to base currency |

Example:

```json
{
  "status": 1,
  "data": {
    "gain_loss": 1234.56,
    "items": [
      {
        "action_main": "EXP01",
        "action_main_table": "Code_Data",
        "action_main_type": "expense",
        "distinct_number": 1,
        "note": "Lunch",
        "spend_date": "20260418",
        "spend_way": "1",
        "spend_way_table": "Account",
        "spend_way_type": "account",
        "spending": -123.45,
        "vesting_month": "202604"
      }
    ]
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
