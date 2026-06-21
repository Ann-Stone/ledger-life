"""Journal CRUD + analytics endpoints (Monthly Report domain)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.models.monthly_report.analytics import (
    ExpenditureBudgetResponse,
    ExpenditureRatioResponse,
    InvestRatioResponse,
    LiabilityResponse,
    UncategorizedSummaryResponse,
)
from app.models.assets.estate import EstateJournalRead
from app.models.assets.insurance import InsuranceJournalRead
from app.models.assets.loan import LoanJournalRead
from app.models.assets.stock import StockDetailRead
from app.models.monthly_report.journal import (
    Journal,
    JournalCreate,
    JournalMonthRead,
    JournalRead,
    JournalUpdate,
)
from app.models.monthly_report.journal_composite import (
    JournalEstateTransactionCreate,
    JournalEstateTransactionRead,
    JournalEstateTransactionUpdate,
    JournalInsuranceTransactionCreate,
    JournalInsuranceTransactionRead,
    JournalInsuranceTransactionUpdate,
    JournalLoanTransactionCreate,
    JournalLoanTransactionRead,
    JournalLoanTransactionUpdate,
    JournalStockTransactionCreate,
    JournalStockTransactionRead,
    JournalStockTransactionUpdate,
)
from app.schemas.response import (
    INTERNAL_ERROR,
    VALIDATION_ERROR,
    ApiResponse,
    error_response,
    not_found_error,
)
from app.services.monthly_report_service import (
    compute_expenditure_budget,
    compute_expenditure_ratio,
    compute_gain_loss,
    compute_invest_ratio,
    compute_liability,
    compute_uncategorized_summary,
    create_journal,
    create_journal_with_estate_transaction,
    create_journal_with_insurance_transaction,
    create_journal_with_loan_transaction,
    create_journal_with_stock_transaction,
    delete_journal,
    list_journals_by_month,
    update_journal,
    update_journal_with_estate_transaction,
    update_journal_with_insurance_transaction,
    update_journal_with_loan_transaction,
    update_journal_with_stock_transaction,
)

router = APIRouter()


# NOTE: must be declared before the catch-all ``/{vesting_month}`` route, or
# FastAPI would try to parse "uncategorized-summary" as a month.
@router.get(
    "/uncategorized-summary",
    summary="Count uncategorized journals across all months",
    description=(
        "Return the total number of Journal rows whose action_main_type falls "
        "outside every report bucket (expense/income/invest/transfer — e.g. "
        "legacy 'undefined'/'No'/'' values), plus a per-month breakdown "
        "ordered newest first. Months with zero uncategorized rows are omitted."
    ),
    response_model=ApiResponse[UncategorizedSummaryResponse],
    responses={500: INTERNAL_ERROR},
)
def get_uncategorized_summary(
    session: Session = Depends(get_session),
) -> ApiResponse[UncategorizedSummaryResponse]:
    return ApiResponse(data=compute_uncategorized_summary(session))


@router.get(
    "/{vesting_month}",
    summary="List journals for a month with gain/loss",
    description=(
        "Return all Journal entries whose vesting_month matches the path parameter, "
        "ordered by spend_date. The response also includes the FX-converted gain/loss "
        "total for the month."
    ),
    response_model=ApiResponse[JournalMonthRead],
    responses={422: VALIDATION_ERROR, 500: INTERNAL_ERROR},
)
def get_journals_by_month(
    vesting_month: str, session: Session = Depends(get_session)
) -> ApiResponse[JournalMonthRead]:
    journals = list_journals_by_month(session, vesting_month)
    gain_loss = compute_gain_loss(session, journals)
    payload = JournalMonthRead(
        items=[JournalRead.model_validate(j, from_attributes=True) for j in journals],
        gain_loss=gain_loss,
    )
    return ApiResponse(data=payload)


@router.post(
    "",
    summary="Create a journal entry",
    description="Persist a new Journal row. distinct_number is auto-assigned.",
    response_model=ApiResponse[JournalRead],
    status_code=201,
    responses={
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def post_journal(
    payload: JournalCreate, session: Session = Depends(get_session)
) -> ApiResponse[JournalRead]:
    row = create_journal(session, payload)
    return ApiResponse(data=JournalRead.model_validate(row, from_attributes=True))


@router.post(
    "/stock-transaction",
    summary="Create a journal entry + stock transaction atomically",
    description=(
        "Persist a Journal row and a Stock_Detail row in a single database "
        "transaction. excute_price is copied verbatim from journal.spending "
        "(sign preserved); account_id/account_name are resolved from "
        "journal.spend_way (account or credit card)."
    ),
    response_model=ApiResponse[JournalStockTransactionRead],
    status_code=201,
    responses={
        404: error_response(
            "Settling source or stock not found",
            error_payload="Stock not found: STK-H-001",
        ),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def post_journal_stock_transaction(
    payload: JournalStockTransactionCreate,
    session: Session = Depends(get_session),
) -> ApiResponse[JournalStockTransactionRead]:
    journal_row, detail_row = create_journal_with_stock_transaction(session, payload)
    return ApiResponse(
        data=JournalStockTransactionRead(
            journal=JournalRead.model_validate(journal_row, from_attributes=True),
            stock_detail=StockDetailRead.model_validate(detail_row, from_attributes=True),
        )
    )


@router.post(
    "/insurance-transaction",
    summary="Create a journal entry + insurance transaction atomically",
    description=(
        "Persist a Journal row and an Insurance_Journal row in a single database "
        "transaction. excute_price is copied verbatim from journal.spending "
        "(sign preserved). Insurance_Journal stores no payment source, so unlike "
        "the stock variant there is no settling-account lookup."
    ),
    response_model=ApiResponse[JournalInsuranceTransactionRead],
    status_code=201,
    responses={
        404: error_response(
            "Insurance policy not found",
            error_payload="Insurance not found: INS-001",
        ),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def post_journal_insurance_transaction(
    payload: JournalInsuranceTransactionCreate,
    session: Session = Depends(get_session),
) -> ApiResponse[JournalInsuranceTransactionRead]:
    journal_row, detail_row = create_journal_with_insurance_transaction(session, payload)
    return ApiResponse(
        data=JournalInsuranceTransactionRead(
            journal=JournalRead.model_validate(journal_row, from_attributes=True),
            insurance_detail=InsuranceJournalRead.model_validate(
                detail_row, from_attributes=True
            ),
        )
    )


@router.post(
    "/estate-transaction",
    summary="Create a journal entry + estate transaction atomically",
    description=(
        "Persist a Journal row and an Estate_Journal row in a single database "
        "transaction. excute_price is copied verbatim from journal.spending "
        "(sign preserved). Estate_Journal stores no payment source, so unlike "
        "the stock variant there is no settling-account lookup."
    ),
    response_model=ApiResponse[JournalEstateTransactionRead],
    status_code=201,
    responses={
        404: error_response(
            "Estate not found",
            error_payload="Estate not found: EST-001",
        ),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def post_journal_estate_transaction(
    payload: JournalEstateTransactionCreate,
    session: Session = Depends(get_session),
) -> ApiResponse[JournalEstateTransactionRead]:
    journal_row, detail_row = create_journal_with_estate_transaction(session, payload)
    return ApiResponse(
        data=JournalEstateTransactionRead(
            journal=JournalRead.model_validate(journal_row, from_attributes=True),
            estate_detail=EstateJournalRead.model_validate(
                detail_row, from_attributes=True
            ),
        )
    )


@router.post(
    "/loan-transaction",
    summary="Create a journal entry + loan repayment (principal/interest) atomically",
    description=(
        "Persist a Journal row and its Loan_Journal rows in a single database "
        "transaction. The repayment splits into a principal portion and an "
        "interest portion, each stored as a positive magnitude (NOT a signed "
        "copy of journal.spending); journal.spending is the signed total outflow "
        "and must equal −(principal+interest). Loan_Journal stores no payment "
        "source, so unlike the stock variant there is no settling-account lookup."
    ),
    response_model=ApiResponse[JournalLoanTransactionRead],
    status_code=201,
    responses={
        404: error_response("Loan not found", error_payload="Loan not found: LN-001"),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def post_journal_loan_transaction(
    payload: JournalLoanTransactionCreate,
    session: Session = Depends(get_session),
) -> ApiResponse[JournalLoanTransactionRead]:
    journal_row, detail_rows = create_journal_with_loan_transaction(session, payload)
    return ApiResponse(
        data=JournalLoanTransactionRead(
            journal=JournalRead.model_validate(journal_row, from_attributes=True),
            loan_details=[
                LoanJournalRead.model_validate(r, from_attributes=True)
                for r in detail_rows
            ],
        )
    )


@router.put(
    "/{journal_id}/stock-transaction",
    summary="Update a journal entry + create stock transaction atomically",
    description=(
        "Apply a partial Journal update and insert a brand-new Stock_Detail row "
        "in a single database transaction. Intended for the case where a journal "
        "was originally untagged (action_sub null) and is being re-classified as "
        "a stock transaction. Both writes succeed or both roll back."
    ),
    response_model=ApiResponse[JournalStockTransactionRead],
    responses={
        404: error_response(
            "Journal, settling source, or stock not found",
            error_payload="Journal not found: 42",
        ),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def put_journal_stock_transaction(
    journal_id: int,
    payload: JournalStockTransactionUpdate,
    session: Session = Depends(get_session),
) -> ApiResponse[JournalStockTransactionRead]:
    journal_row, detail_row = update_journal_with_stock_transaction(
        session, journal_id, payload
    )
    return ApiResponse(
        data=JournalStockTransactionRead(
            journal=JournalRead.model_validate(journal_row, from_attributes=True),
            stock_detail=StockDetailRead.model_validate(detail_row, from_attributes=True),
        )
    )


@router.put(
    "/{journal_id}/insurance-transaction",
    summary="Update a journal entry + create insurance transaction atomically",
    description=(
        "Apply a partial Journal update and insert a brand-new Insurance_Journal "
        "row in a single database transaction. Intended for re-classifying a "
        "previously-untagged journal (action_sub null) as an insurance "
        "transaction. Both writes succeed or both roll back."
    ),
    response_model=ApiResponse[JournalInsuranceTransactionRead],
    responses={
        404: error_response(
            "Journal or insurance policy not found",
            error_payload="Journal not found: 42",
        ),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def put_journal_insurance_transaction(
    journal_id: int,
    payload: JournalInsuranceTransactionUpdate,
    session: Session = Depends(get_session),
) -> ApiResponse[JournalInsuranceTransactionRead]:
    journal_row, detail_row = update_journal_with_insurance_transaction(
        session, journal_id, payload
    )
    return ApiResponse(
        data=JournalInsuranceTransactionRead(
            journal=JournalRead.model_validate(journal_row, from_attributes=True),
            insurance_detail=InsuranceJournalRead.model_validate(
                detail_row, from_attributes=True
            ),
        )
    )


@router.put(
    "/{journal_id}/estate-transaction",
    summary="Update a journal entry + create estate transaction atomically",
    description=(
        "Apply a partial Journal update and insert a brand-new Estate_Journal row "
        "in a single database transaction. Intended for re-classifying a "
        "previously-untagged journal (action_sub null) as an estate transaction. "
        "Both writes succeed or both roll back."
    ),
    response_model=ApiResponse[JournalEstateTransactionRead],
    responses={
        404: error_response(
            "Journal or estate not found",
            error_payload="Journal not found: 42",
        ),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def put_journal_estate_transaction(
    journal_id: int,
    payload: JournalEstateTransactionUpdate,
    session: Session = Depends(get_session),
) -> ApiResponse[JournalEstateTransactionRead]:
    journal_row, detail_row = update_journal_with_estate_transaction(
        session, journal_id, payload
    )
    return ApiResponse(
        data=JournalEstateTransactionRead(
            journal=JournalRead.model_validate(journal_row, from_attributes=True),
            estate_detail=EstateJournalRead.model_validate(
                detail_row, from_attributes=True
            ),
        )
    )


@router.put(
    "/{journal_id}/loan-transaction",
    summary="Update a journal entry + create loan repayment rows atomically",
    description=(
        "Apply a partial Journal update and insert fresh Loan_Journal rows "
        "(principal/interest) in a single database transaction. Intended for "
        "re-classifying a previously-untagged journal as a loan repayment. Both "
        "writes succeed or both roll back."
    ),
    response_model=ApiResponse[JournalLoanTransactionRead],
    responses={
        404: error_response(
            "Journal or loan not found", error_payload="Journal not found: 42"
        ),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def put_journal_loan_transaction(
    journal_id: int,
    payload: JournalLoanTransactionUpdate,
    session: Session = Depends(get_session),
) -> ApiResponse[JournalLoanTransactionRead]:
    journal_row, detail_rows = update_journal_with_loan_transaction(
        session, journal_id, payload
    )
    return ApiResponse(
        data=JournalLoanTransactionRead(
            journal=JournalRead.model_validate(journal_row, from_attributes=True),
            loan_details=[
                LoanJournalRead.model_validate(r, from_attributes=True)
                for r in detail_rows
            ],
        )
    )


@router.put(
    "/{journal_id}",
    summary="Update a journal entry",
    description="Partial update of a Journal identified by distinct_number.",
    response_model=ApiResponse[JournalRead],
    responses={
        404: not_found_error("Journal"),
        422: VALIDATION_ERROR,
        500: INTERNAL_ERROR,
    },
)
def put_journal(
    journal_id: int,
    payload: JournalUpdate,
    session: Session = Depends(get_session),
) -> ApiResponse[JournalRead]:
    row = update_journal(session, journal_id, payload)
    return ApiResponse(data=JournalRead.model_validate(row, from_attributes=True))


@router.delete(
    "/{journal_id}",
    summary="Delete a journal entry",
    description="Delete a Journal identified by distinct_number.",
    response_model=ApiResponse[dict],
    responses={
        422: VALIDATION_ERROR,
        404: not_found_error("Journal"),
        500: INTERNAL_ERROR,
    },
)
def delete_journal_endpoint(
    journal_id: int, session: Session = Depends(get_session)
) -> ApiResponse[dict]:
    delete_journal(session, journal_id)
    return ApiResponse(data={"deleted": journal_id})


# ---------- Analytics (BE-017) ----------


@router.get(
    "/{vesting_month}/expenditure-ratio",
    summary="Monthly expenditure ratio (inner/outer pie)",
    description=(
        "Return outer/inner aggregations of journal spending for the given month. "
        "Outer = grouped by action_main_type; inner = grouped by action_sub_type. "
        "Excludes 'invest' and 'transfer' main types."
    ),
    response_model=ApiResponse[ExpenditureRatioResponse],
    responses={
        422: VALIDATION_ERROR,
        404: error_response("No data for the month", error_payload="No data for the month"),
        500: INTERNAL_ERROR,
    },
)
def get_expenditure_ratio(
    vesting_month: str, session: Session = Depends(get_session)
) -> ApiResponse[ExpenditureRatioResponse]:
    return ApiResponse(data=compute_expenditure_ratio(session, vesting_month))


@router.get(
    "/{vesting_month}/invest-ratio",
    summary="Monthly invest ratio",
    description="Aggregate journal spending whose action_main_type == 'invest', grouped by action_sub_type.",
    response_model=ApiResponse[InvestRatioResponse],
    responses={
        422: VALIDATION_ERROR,
        404: error_response("No data for the month", error_payload="No data for the month"),
        500: INTERNAL_ERROR,
    },
)
def get_invest_ratio(
    vesting_month: str, session: Session = Depends(get_session)
) -> ApiResponse[InvestRatioResponse]:
    return ApiResponse(data=compute_invest_ratio(session, vesting_month))


@router.get(
    "/{vesting_month}/expenditure-budget",
    summary="Actual vs budget per category",
    description=(
        "Compare expected (Budget.expected<MM>) vs actual (Journal.spending sum) per "
        "category, returning diff and usage_rate."
    ),
    response_model=ApiResponse[ExpenditureBudgetResponse],
    responses={
        422: VALIDATION_ERROR,
        404: error_response("No data for the month", error_payload="No data for the month"),
        500: INTERNAL_ERROR,
    },
)
def get_expenditure_budget(
    vesting_month: str, session: Session = Depends(get_session)
) -> ApiResponse[ExpenditureBudgetResponse]:
    return ApiResponse(data=compute_expenditure_budget(session, vesting_month))


@router.get(
    "/{vesting_month}/liability",
    summary="Credit-card liability breakdown",
    description="Aggregate journal spending whose spend_way_type == 'credit_card', grouped by credit card.",
    response_model=ApiResponse[LiabilityResponse],
    responses={
        422: VALIDATION_ERROR,
        404: error_response("No data for the month", error_payload="No data for the month"),
        500: INTERNAL_ERROR,
    },
)
def get_liability(
    vesting_month: str, session: Session = Depends(get_session)
) -> ApiResponse[LiabilityResponse]:
    return ApiResponse(data=compute_liability(session, vesting_month))


__all__ = ["router"]
