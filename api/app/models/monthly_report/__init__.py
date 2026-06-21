"""Monthly Report domain SQLModel tables + CRUD schemas."""
from app.models.monthly_report.account_balance import (
    AccountBalance,
    AccountBalanceCreate,
    AccountBalanceRead,
    AccountBalanceUpdate,
)
from app.models.monthly_report.credit_card_balance import (
    CreditCardBalance,
    CreditCardBalanceCreate,
    CreditCardBalanceRead,
    CreditCardBalanceUpdate,
)
from app.models.monthly_report.estate_net_value_history import (
    EstateNetValueHistory,
    EstateNetValueHistoryCreate,
    EstateNetValueHistoryRead,
    EstateNetValueHistoryUpdate,
)
from app.models.monthly_report.insurance_net_value_history import (
    InsuranceNetValueHistory,
    InsuranceNetValueHistoryCreate,
    InsuranceNetValueHistoryRead,
    InsuranceNetValueHistoryUpdate,
)
from app.models.monthly_report.journal import (
    Journal,
    JournalCreate,
    JournalMonthRead,
    JournalRead,
    JournalUpdate,
)
from app.models.monthly_report.loan_balance import (
    LoanBalance,
    LoanBalanceCreate,
    LoanBalanceRead,
    LoanBalanceUpdate,
)
from app.models.monthly_report.stock_net_value_history import (
    StockNetValueHistory,
    StockNetValueHistoryCreate,
    StockNetValueHistoryRead,
    StockNetValueHistoryUpdate,
)

__all__ = [
    "AccountBalance",
    "AccountBalanceCreate",
    "AccountBalanceRead",
    "AccountBalanceUpdate",
    "CreditCardBalance",
    "CreditCardBalanceCreate",
    "CreditCardBalanceRead",
    "CreditCardBalanceUpdate",
    "EstateNetValueHistory",
    "EstateNetValueHistoryCreate",
    "EstateNetValueHistoryRead",
    "EstateNetValueHistoryUpdate",
    "InsuranceNetValueHistory",
    "InsuranceNetValueHistoryCreate",
    "InsuranceNetValueHistoryRead",
    "InsuranceNetValueHistoryUpdate",
    "Journal",
    "JournalCreate",
    "JournalMonthRead",
    "JournalRead",
    "JournalUpdate",
    "LoanBalance",
    "LoanBalanceCreate",
    "LoanBalanceRead",
    "LoanBalanceUpdate",
    "StockNetValueHistory",
    "StockNetValueHistoryCreate",
    "StockNetValueHistoryRead",
    "StockNetValueHistoryUpdate",
]
