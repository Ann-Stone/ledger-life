"""Cash-flow statement (現金流量表) response schemas — Reports domain.

Personal cash flow split into three activities, mirroring the standard statement:
operating (生活: income − living expenses − loan interest), investing (投資:
buy/sell of holdings), financing (債務: loan principal repayment / new borrowing).
Self-transfers are excluded (net-zero); credit-card spend is counted once as an
operating outflow and never re-counted at settlement. All amounts are
FX-converted and signed (positive = cash in, negative = cash out).

Shaped like the income statement (``{type, points, summary}``): ``points`` is a
per-period series for the trend chart, while ``summary`` carries the window-level
activity breakdown (with signed sub-items) for the cards / waterfall / tree.
Unlike the income statement there is no floor-at-0 / cross-month netting, so each
period is independent and the summary equals the sum of the points.
"""
from __future__ import annotations

from typing import Literal

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

_ITEM_EXAMPLE = {"label": "收入", "amount": 960000.0}


class CashFlowItem(SQLModel):
    label: str = Field(..., description="Component label", schema_extra={"examples": ["收入"]})
    amount: float = Field(
        ...,
        description="Signed cash flow (positive = in, negative = out)",
        schema_extra={"examples": [960000.0]},
    )

    model_config = ConfigDict(json_schema_extra={"example": _ITEM_EXAMPLE})


_ACTIVITY_EXAMPLE = {
    "key": "operating",
    "label": "生活",
    "net": 444000.0,
    "items": [_ITEM_EXAMPLE, {"label": "生活支出", "amount": -516000.0}],
}


class CashFlowActivity(SQLModel):
    key: str = Field(
        ..., description="operating | investing | financing", schema_extra={"examples": ["operating"]}
    )
    label: str = Field(
        ..., description="Display label: 生活 / 投資 / 債務", schema_extra={"examples": ["生活"]}
    )
    net: float = Field(
        ..., description="Signed net cash flow for the activity", schema_extra={"examples": [444000.0]}
    )
    items: list[CashFlowItem] = Field(
        ..., description="Signed sub-components", schema_extra={"examples": [[_ITEM_EXAMPLE]]}
    )

    model_config = ConfigDict(json_schema_extra={"example": _ACTIVITY_EXAMPLE})


_POINT_EXAMPLE = {
    "period": "202403",
    "operating": 37000.0,
    "investing": -15000.0,
    "financing": -7000.0,
    "net_change": 15000.0,
}


class CashFlowPoint(SQLModel):
    period: str = Field(
        ...,
        description="YYYYMM for monthly or YYYY for yearly",
        schema_extra={"examples": ["202403"]},
    )
    operating: float = Field(
        ...,
        description="生活 net for the period (income − living − loan interest), signed",
        schema_extra={"examples": [37000.0]},
    )
    investing: float = Field(
        ...,
        description="投資 net for the period (buy negative, sell positive), signed",
        schema_extra={"examples": [-15000.0]},
    )
    financing: float = Field(
        ...,
        description="債務 net for the period (new borrowing − principal repayment), signed",
        schema_extra={"examples": [-7000.0]},
    )
    net_change: float = Field(
        ...,
        description="operating + investing + financing for the period, signed",
        schema_extra={"examples": [15000.0]},
    )

    model_config = ConfigDict(json_schema_extra={"example": _POINT_EXAMPLE})


_SUMMARY_EXAMPLE = {
    "activities": [_ACTIVITY_EXAMPLE],
    "net_change": 123000.0,
}


class CashFlowSummary(SQLModel):
    activities: list[CashFlowActivity] = Field(
        ...,
        description="[operating, investing, financing] in order, with signed sub-items",
        schema_extra={"examples": [[_ACTIVITY_EXAMPLE]]},
    )
    net_change: float = Field(
        ...,
        description="Sum of the three activities' net flows across the window (overall change in cash)",
        schema_extra={"examples": [123000.0]},
    )

    model_config = ConfigDict(json_schema_extra={"example": _SUMMARY_EXAMPLE})


class CashFlowRead(SQLModel):
    type: Literal["monthly", "yearly"] = Field(
        ..., description="Aggregation granularity", schema_extra={"examples": ["monthly"]}
    )
    points: list[CashFlowPoint] = Field(
        ...,
        description="Per-period cash-flow series, oldest first",
        schema_extra={"examples": [[_POINT_EXAMPLE]]},
    )
    summary: CashFlowSummary = Field(
        ..., description="Window-level activity breakdown + overall net change"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "monthly",
                "points": [_POINT_EXAMPLE],
                "summary": _SUMMARY_EXAMPLE,
            }
        }
    )
