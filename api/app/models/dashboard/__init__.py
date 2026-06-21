"""Dashboard domain models."""
from app.models.dashboard.alarm_view import AlarmItem
from app.models.dashboard.budget import BudgetLine, BudgetRead, BudgetType
from app.models.dashboard.gift_view import GiftItem
from app.models.dashboard.fx_rate import FXRate, FXRateCreate, FXRateRead, FXRateUpdate
from app.models.dashboard.house_price_index import (
    EstateValueSuggestion,
    HousePriceIndex,
    HousePriceIndexRead,
    IndexRefreshResult,
)
from app.models.dashboard.stock_price_history import (
    StockPriceHistory,
    StockPriceHistoryCreate,
    StockPriceHistoryRead,
    StockPriceHistoryUpdate,
)
from app.models.dashboard.retirement import (
    LoanPayoff,
    RetirementReadinessRead,
    RetirementSetting,
    RetirementSettingRead,
    RetirementSettingUpdate,
)
from app.models.dashboard.summary import SummaryPoint, SummaryRead, SummaryType
from app.models.dashboard.target_setting import (
    TargetSetting,
    TargetSettingCreate,
    TargetSettingRead,
    TargetSettingUpdate,
)

__all__ = [
    "LoanPayoff",
    "RetirementReadinessRead",
    "RetirementSetting",
    "RetirementSettingRead",
    "RetirementSettingUpdate",
    "AlarmItem",
    "GiftItem",
    "BudgetLine",
    "BudgetRead",
    "BudgetType",
    "FXRate",
    "FXRateCreate",
    "FXRateUpdate",
    "FXRateRead",
    "EstateValueSuggestion",
    "HousePriceIndex",
    "HousePriceIndexRead",
    "IndexRefreshResult",
    "StockPriceHistory",
    "StockPriceHistoryCreate",
    "StockPriceHistoryUpdate",
    "StockPriceHistoryRead",
    "SummaryPoint",
    "SummaryRead",
    "SummaryType",
    "TargetSetting",
    "TargetSettingCreate",
    "TargetSettingUpdate",
    "TargetSettingRead",
]
