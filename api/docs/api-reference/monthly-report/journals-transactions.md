# Monthly Report — Journals Transactions

Generated from the live FastAPI OpenAPI spec by `uv run export-docs`. Do not edit by hand.

## Endpoints

### POST /monthly-report/journals/estate-transaction

**Create a journal entry + estate transaction atomically**

Persist a Journal row and an Estate_Journal row in a single database transaction. excute_price is copied verbatim from journal.spending (sign preserved). Estate_Journal stores no payment source, so unlike the stock variant there is no settling-account lookup.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| journal | JournalCreate | yes | Journal row to insert. |
| estate_detail | EstateTransactionDetailCreate | yes | Estate detail row derived from + linked to the journal. |

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
| journal | JournalRead | yes | Persisted journal row. |
| estate_detail | EstateJournalRead | yes | Persisted estate detail row. |

Example:

```json
{
  "status": 1,
  "data": {
    "estate_detail": {
      "distinct_number": 17,
      "estate_excute_type": "tax",
      "estate_id": "EST-001",
      "excute_date": "20260115",
      "excute_price": -8000.0,
      "memo": "Property tax"
    },
    "journal": {
      "action_main": "TRA",
      "action_main_table": "Code_Data",
      "action_main_type": "Transfer",
      "action_sub": "Estate",
      "action_sub_table": "Estate_Journal",
      "action_sub_type": "Asset",
      "distinct_number": 42,
      "note": "Property tax",
      "spend_date": "20260115",
      "spend_way": "1",
      "spend_way_table": "Account",
      "spend_way_type": "account",
      "spending": -8000.0,
      "vesting_month": "202601"
    }
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Estate not found | `{"status": 0, "error": "Estate not found: EST-001", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### POST /monthly-report/journals/insurance-transaction

**Create a journal entry + insurance transaction atomically**

Persist a Journal row and an Insurance_Journal row in a single database transaction. excute_price is copied verbatim from journal.spending (sign preserved). Insurance_Journal stores no payment source, so unlike the stock variant there is no settling-account lookup.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| journal | JournalCreate | yes | Journal row to insert. |
| insurance_detail | InsuranceTransactionDetailCreate | yes | Insurance detail row derived from + linked to the journal. |

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
| journal | JournalRead | yes | Persisted journal row. |
| insurance_detail | InsuranceJournalRead | yes | Persisted insurance detail row. |

Example:

```json
{
  "status": 1,
  "data": {
    "insurance_detail": {
      "distinct_number": 17,
      "excute_date": "20260115",
      "excute_price": -1200.0,
      "insurance_excute_type": "pay",
      "insurance_id": "INS-001",
      "memo": "Annual premium"
    },
    "journal": {
      "action_main": "TRA",
      "action_main_table": "Code_Data",
      "action_main_type": "Transfer",
      "action_sub": "Insurance",
      "action_sub_table": "Insurance_Journal",
      "action_sub_type": "Asset",
      "distinct_number": 42,
      "note": "Annual premium",
      "spend_date": "20260115",
      "spend_way": "1",
      "spend_way_table": "Account",
      "spend_way_type": "account",
      "spending": -1200.0,
      "vesting_month": "202601"
    }
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Insurance policy not found | `{"status": 0, "error": "Insurance not found: INS-001", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### POST /monthly-report/journals/loan-transaction

**Create a journal entry + loan repayment (principal/interest) atomically**

Persist a Journal row and its Loan_Journal rows in a single database transaction. The repayment splits into a principal portion and an interest portion, each stored as a positive magnitude (NOT a signed copy of journal.spending); journal.spending is the signed total outflow and must equal −(principal+interest). Loan_Journal stores no payment source, so unlike the stock variant there is no settling-account lookup.

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| journal | JournalCreate | yes | Journal row to insert. |
| loan_detail | LoanTransactionDetailCreate | yes | Loan repayment split derived from + linked to the journal. |

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
| journal | JournalRead | yes | Persisted journal row. |
| loan_details | array<LoanJournalRead> | yes | Persisted Loan_Journal rows (principal and/or interest). |

Example:

```json
{
  "status": 1,
  "data": {
    "journal": {
      "action_main": "LoanRepayment",
      "action_main_table": "Loan",
      "action_main_type": "LoanRepayment",
      "action_sub": "LN-001",
      "action_sub_table": "Loan",
      "action_sub_type": "Loan",
      "distinct_number": 42,
      "note": "April mortgage payment",
      "spend_date": "20260401",
      "spend_way": "1",
      "spend_way_table": "Account",
      "spend_way_type": "account",
      "spending": -9200.0,
      "vesting_month": "202604"
    },
    "loan_details": [
      {
        "distinct_number": 17,
        "excute_date": "20260401",
        "excute_price": 8000.0,
        "loan_excute_type": "principal",
        "loan_id": "LN-001",
        "memo": "April payment"
      },
      {
        "distinct_number": 18,
        "excute_date": "20260401",
        "excute_price": 1200.0,
        "loan_excute_type": "interest",
        "loan_id": "LN-001",
        "memo": "April payment"
      }
    ]
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Loan not found | `{"status": 0, "error": "Loan not found: LN-001", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### POST /monthly-report/journals/stock-transaction

**Create a journal entry + stock transaction atomically**

Persist a Journal row and a Stock_Detail row in a single database transaction. excute_price is copied verbatim from journal.spending (sign preserved); account_id/account_name are resolved from journal.spend_way (account or credit card).

#### Request

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| journal | JournalCreate | yes | Journal row to insert. |
| stock_detail | StockTransactionDetailCreate | yes | Stock detail row derived from + linked to the journal. |

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
| journal | JournalRead | yes | Persisted journal row. |
| stock_detail | StockDetailRead | yes | Persisted stock detail row. |

Example:

```json
{
  "status": 1,
  "data": {
    "journal": {
      "action_main": "INV01",
      "action_main_table": "Code_Data",
      "action_main_type": "Invest",
      "distinct_number": 42,
      "note": "Buy AAPL",
      "spend_date": "20260418",
      "spend_way": "1",
      "spend_way_table": "Account",
      "spend_way_type": "account",
      "spending": -1805.0,
      "vesting_month": "202604"
    },
    "stock_detail": {
      "account_id": "BANK-CHASE-01",
      "account_name": "Chase Checking",
      "distinct_number": 17,
      "excute_amount": 10.0,
      "excute_date": "20260418",
      "excute_price": -1805.0,
      "excute_type": "buy",
      "memo": "First lot",
      "stock_id": "STK-H-001"
    }
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Settling source or stock not found | `{"status": 0, "error": "Stock not found: STK-H-001", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### PUT /monthly-report/journals/{journal_id}/estate-transaction

**Update a journal entry + create estate transaction atomically**

Apply a partial Journal update and insert a brand-new Estate_Journal row in a single database transaction. Intended for re-classifying a previously-untagged journal (action_sub null) as an estate transaction. Both writes succeed or both roll back.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| journal_id | path | integer | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| journal | JournalUpdate | yes | Journal fields to update. |
| estate_detail | EstateTransactionDetailCreate | yes | Estate detail row to insert alongside the update. |

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
| journal | JournalRead | yes | Persisted journal row. |
| estate_detail | EstateJournalRead | yes | Persisted estate detail row. |

Example:

```json
{
  "status": 1,
  "data": {
    "estate_detail": {
      "distinct_number": 17,
      "estate_excute_type": "tax",
      "estate_id": "EST-001",
      "excute_date": "20260115",
      "excute_price": -8000.0,
      "memo": "Property tax"
    },
    "journal": {
      "action_main": "TRA",
      "action_main_table": "Code_Data",
      "action_main_type": "Transfer",
      "action_sub": "Estate",
      "action_sub_table": "Estate_Journal",
      "action_sub_type": "Asset",
      "distinct_number": 42,
      "note": "Property tax",
      "spend_date": "20260115",
      "spend_way": "1",
      "spend_way_table": "Account",
      "spend_way_type": "account",
      "spending": -8000.0,
      "vesting_month": "202601"
    }
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Journal or estate not found | `{"status": 0, "error": "Journal not found: 42", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### PUT /monthly-report/journals/{journal_id}/insurance-transaction

**Update a journal entry + create insurance transaction atomically**

Apply a partial Journal update and insert a brand-new Insurance_Journal row in a single database transaction. Intended for re-classifying a previously-untagged journal (action_sub null) as an insurance transaction. Both writes succeed or both roll back.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| journal_id | path | integer | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| journal | JournalUpdate | yes | Journal fields to update. |
| insurance_detail | InsuranceTransactionDetailCreate | yes | Insurance detail row to insert alongside the update. |

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
| journal | JournalRead | yes | Persisted journal row. |
| insurance_detail | InsuranceJournalRead | yes | Persisted insurance detail row. |

Example:

```json
{
  "status": 1,
  "data": {
    "insurance_detail": {
      "distinct_number": 17,
      "excute_date": "20260115",
      "excute_price": -1200.0,
      "insurance_excute_type": "pay",
      "insurance_id": "INS-001",
      "memo": "Annual premium"
    },
    "journal": {
      "action_main": "TRA",
      "action_main_table": "Code_Data",
      "action_main_type": "Transfer",
      "action_sub": "Insurance",
      "action_sub_table": "Insurance_Journal",
      "action_sub_type": "Asset",
      "distinct_number": 42,
      "note": "Annual premium",
      "spend_date": "20260115",
      "spend_way": "1",
      "spend_way_table": "Account",
      "spend_way_type": "account",
      "spending": -1200.0,
      "vesting_month": "202601"
    }
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Journal or insurance policy not found | `{"status": 0, "error": "Journal not found: 42", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### PUT /monthly-report/journals/{journal_id}/loan-transaction

**Update a journal entry + create loan repayment rows atomically**

Apply a partial Journal update and insert fresh Loan_Journal rows (principal/interest) in a single database transaction. Intended for re-classifying a previously-untagged journal as a loan repayment. Both writes succeed or both roll back.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| journal_id | path | integer | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| journal | JournalUpdate | yes | Journal fields to update. |
| loan_detail | LoanTransactionDetailCreate | yes | Loan repayment split to insert alongside the update. |

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
| journal | JournalRead | yes | Persisted journal row. |
| loan_details | array<LoanJournalRead> | yes | Persisted Loan_Journal rows (principal and/or interest). |

Example:

```json
{
  "status": 1,
  "data": {
    "journal": {
      "action_main": "LoanRepayment",
      "action_main_table": "Loan",
      "action_main_type": "LoanRepayment",
      "action_sub": "LN-001",
      "action_sub_table": "Loan",
      "action_sub_type": "Loan",
      "distinct_number": 42,
      "note": "April mortgage payment",
      "spend_date": "20260401",
      "spend_way": "1",
      "spend_way_table": "Account",
      "spend_way_type": "account",
      "spending": -9200.0,
      "vesting_month": "202604"
    },
    "loan_details": [
      {
        "distinct_number": 17,
        "excute_date": "20260401",
        "excute_price": 8000.0,
        "loan_excute_type": "principal",
        "loan_id": "LN-001",
        "memo": "April payment"
      },
      {
        "distinct_number": 18,
        "excute_date": "20260401",
        "excute_price": 1200.0,
        "loan_excute_type": "interest",
        "loan_id": "LN-001",
        "memo": "April payment"
      }
    ]
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Journal or loan not found | `{"status": 0, "error": "Journal not found: 42", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |

### PUT /monthly-report/journals/{journal_id}/stock-transaction

**Update a journal entry + create stock transaction atomically**

Apply a partial Journal update and insert a brand-new Stock_Detail row in a single database transaction. Intended for the case where a journal was originally untagged (action_sub null) and is being re-classified as a stock transaction. Both writes succeed or both roll back.

#### Request

| name | in | type | required | description |
| --- | --- | --- | --- | --- |
| journal_id | path | integer | yes |  |

Body:

| name | type | required | description |
| --- | --- | --- | --- |
| journal | JournalUpdate | yes | Journal fields to update. |
| stock_detail | StockTransactionDetailCreate | yes | Stock detail row to insert alongside the update. |

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
| journal | JournalRead | yes | Persisted journal row. |
| stock_detail | StockDetailRead | yes | Persisted stock detail row. |

Example:

```json
{
  "status": 1,
  "data": {
    "journal": {
      "action_main": "INV01",
      "action_main_table": "Code_Data",
      "action_main_type": "Invest",
      "distinct_number": 42,
      "note": "Buy AAPL",
      "spend_date": "20260418",
      "spend_way": "1",
      "spend_way_table": "Account",
      "spend_way_type": "account",
      "spending": -1805.0,
      "vesting_month": "202604"
    },
    "stock_detail": {
      "account_id": "BANK-CHASE-01",
      "account_name": "Chase Checking",
      "distinct_number": 17,
      "excute_amount": 10.0,
      "excute_date": "20260418",
      "excute_price": -1805.0,
      "excute_type": "buy",
      "memo": "First lot",
      "stock_id": "STK-H-001"
    }
  },
  "msg": "success"
}
```

#### Errors

| status | description | example |
| --- | --- | --- |
| 404 | Journal, settling source, or stock not found | `{"status": 0, "error": "Journal not found: 42", "msg": "fail"}` |
| 422 | Validation error — request payload failed Pydantic validation | `{"status": 0, "error": [{"type": "missing", "loc": ["body", "field_name"], "msg": "Field required", "input": {}}], "msg": "fail"}` |
| 500 | Unhandled server error — wrapped by global exception handler | `{"status": 0, "error": "RuntimeError: unexpected failure", "msg": "fail"}` |
