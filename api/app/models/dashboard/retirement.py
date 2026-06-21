"""Retirement-readiness models — Dashboard domain.

A point-in-time readiness assessment, deliberately kept on the *consumption*
basis: the perpetual target is sized from recurring living expenses (loan
repayment **excluded** — a mortgage is finite and its principal is forced
saving, already counted in net worth). The remaining loan balance is therefore a
finite liability already netted into ``net_worth``; ``loans`` + the
``debt_service_ratio`` give the during-loan cash-flow picture separately.
"""
from __future__ import annotations

from typing import Literal

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

# Single-row settings table: there is exactly one retirement configuration.
_SETTINGS_ROW_ID = 1


class RetirementSetting(SQLModel, table=True):
    """Persisted retirement configuration (single row, ``id == 1``)."""

    __tablename__ = "Retirement_Setting"

    id: int = Field(
        default=_SETTINGS_ROW_ID,
        primary_key=True,
        description="Always 1 — there is a single retirement configuration row",
        schema_extra={"examples": [1]},
    )
    withdrawal_rate: float = Field(
        default=0.04,
        description="Safe withdrawal rate (decimal); target multiple = 1/rate (4% → 25×)",
        schema_extra={"examples": [0.04]},
    )
    annual_expense_override: float | None = Field(
        default=None,
        description=(
            "Optional manual annual retirement expense base (TWD). When null the "
            "base is computed from trailing-12-month consumption (fixed + floating, "
            "loan repayment excluded)."
        ),
        schema_extra={"examples": [600000.0]},
    )
    exclude_self_occupied_estate: bool = Field(
        default=True,
        description=(
            "When true (default), real estate marked self-occupied "
            "(``estate_status == 'live'``) is excluded from the net worth used for "
            "the readiness target — a home you live in cannot fund retirement. No "
            "estate marked 'live' → nothing is excluded."
        ),
        schema_extra={"examples": [True]},
    )


_SETTINGS_EXAMPLE = {
    "withdrawal_rate": 0.04,
    "annual_expense_override": None,
    "exclude_self_occupied_estate": True,
}


class RetirementSettingRead(SQLModel):
    withdrawal_rate: float = Field(
        ..., description="Safe withdrawal rate (decimal)", schema_extra={"examples": [0.04]}
    )
    annual_expense_override: float | None = Field(
        default=None,
        description="Manual annual expense base (TWD), or null to auto-compute",
        schema_extra={"examples": [600000.0]},
    )
    exclude_self_occupied_estate: bool = Field(
        default=True,
        description="Exclude self-occupied (estate_status 'live') housing from retirement net worth",
        schema_extra={"examples": [True]},
    )

    model_config = ConfigDict(json_schema_extra={"example": _SETTINGS_EXAMPLE})


class RetirementSettingUpdate(SQLModel):
    withdrawal_rate: float | None = Field(
        default=None,
        description="New withdrawal rate (decimal, 0.01–0.10); null keeps current",
        schema_extra={"examples": [0.035]},
    )
    annual_expense_override: float | None = Field(
        default=None,
        description="New manual expense base (TWD); null keeps current. Send 0 to clear.",
        schema_extra={"examples": [600000.0]},
    )
    exclude_self_occupied_estate: bool | None = Field(
        default=None,
        description="Toggle excluding self-occupied housing; null keeps current",
        schema_extra={"examples": [True]},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "withdrawal_rate": 0.035,
                "annual_expense_override": None,
                "exclude_self_occupied_estate": True,
            }
        }
    )


_LOAN_PAYOFF_EXAMPLE = {
    "loan_id": "LN-001",
    "loan_name": "房貸",
    "remaining_balance": 3_200_000.0,
    "monthly_payment": 28_000.0,
    "payoff_month": "203406",
    "years_left": 8.5,
}


class LoanPayoff(SQLModel):
    loan_id: str = Field(..., description="Loan business ID", schema_extra={"examples": ["LN-001"]})
    loan_name: str = Field(..., description="Loan display name", schema_extra={"examples": ["房貸"]})
    remaining_balance: float = Field(
        ...,
        description="Outstanding principal (amount − repayed), TWD, positive",
        schema_extra={"examples": [3_200_000.0]},
    )
    monthly_payment: float = Field(
        ...,
        description="Recent average monthly payment (principal + interest), TWD",
        schema_extra={"examples": [28_000.0]},
    )
    payoff_month: str | None = Field(
        default=None,
        description="Projected payoff YYYYMM (from recent principal velocity); null if unknown",
        schema_extra={"examples": ["203406"]},
    )
    years_left: float | None = Field(
        default=None,
        description="Projected years until payoff; null if unknown",
        schema_extra={"examples": [8.5]},
    )

    model_config = ConfigDict(json_schema_extra={"example": _LOAN_PAYOFF_EXAMPLE})


_READINESS_EXAMPLE = {
    "net_worth": 8_000_000.0,
    "exclude_self_occupied_estate": True,
    "self_occupied_estate_value": 0.0,
    "annual_expense_base": 600_000.0,
    "expense_base_source": "computed",
    "withdrawal_rate": 0.04,
    "target_portfolio": 15_000_000.0,
    "readiness_pct": 0.5333,
    "gap": 7_000_000.0,
    "monthly_income": 90_000.0,
    "monthly_loan_payment": 28_000.0,
    "debt_service_ratio": 0.3111,
    "loans": [_LOAN_PAYOFF_EXAMPLE],
}


class RetirementReadinessRead(SQLModel):
    net_worth: float = Field(
        ...,
        description=(
            "Net worth (TWD) used for the readiness target; from the balance sheet "
            "(already nets the loan), minus self-occupied housing when "
            "exclude_self_occupied_estate is on"
        ),
        schema_extra={"examples": [8_000_000.0]},
    )
    exclude_self_occupied_estate: bool = Field(
        ...,
        description="Whether self-occupied (estate_status 'live') housing was excluded from net_worth",
        schema_extra={"examples": [True]},
    )
    self_occupied_estate_value: float = Field(
        ...,
        description=(
            "Self-occupied housing market value excluded from net_worth (TWD); "
            "0 when the toggle is off or no estate is marked 'live'"
        ),
        schema_extra={"examples": [0.0]},
    )
    annual_expense_base: float = Field(
        ...,
        description="Annual retirement expense base (TWD), consumption-basis (loan excluded)",
        schema_extra={"examples": [600_000.0]},
    )
    expense_base_source: Literal["computed", "override"] = Field(
        ...,
        description="'computed' = trailing-12-month consumption; 'override' = manual setting",
        schema_extra={"examples": ["computed"]},
    )
    withdrawal_rate: float = Field(
        ..., description="Safe withdrawal rate used", schema_extra={"examples": [0.04]}
    )
    target_portfolio: float = Field(
        ...,
        description="annual_expense_base / withdrawal_rate (the FIRE number), TWD",
        schema_extra={"examples": [15_000_000.0]},
    )
    readiness_pct: float = Field(
        ...,
        description="net_worth / target_portfolio (≥1.0 means target reached)",
        schema_extra={"examples": [0.5333]},
    )
    gap: float = Field(
        ...,
        description="target_portfolio − net_worth (TWD; ≤0 means surplus)",
        schema_extra={"examples": [7_000_000.0]},
    )
    monthly_income: float = Field(
        ...,
        description="Trailing-12-month average monthly income (TWD)",
        schema_extra={"examples": [90_000.0]},
    )
    monthly_loan_payment: float = Field(
        ...,
        description="Trailing-12-month average monthly loan payment (principal+interest), TWD",
        schema_extra={"examples": [28_000.0]},
    )
    debt_service_ratio: float = Field(
        ...,
        description="monthly_loan_payment / monthly_income (cash-flow health; 0 when no income)",
        schema_extra={"examples": [0.3111]},
    )
    loans: list[LoanPayoff] = Field(
        default_factory=list,
        description="Per-loan remaining balance + projected payoff",
        schema_extra={"examples": [[_LOAN_PAYOFF_EXAMPLE]]},
    )

    model_config = ConfigDict(json_schema_extra={"example": _READINESS_EXAMPLE})
