"""Settings domain SQLModel tables + CRUD schemas."""
from app.models.settings.account import Account, AccountCreate, AccountRead, AccountUpdate
from app.models.settings.alarm import Alarm, AlarmCreate, AlarmRead, AlarmUpdate
from app.models.settings.budget import Budget, BudgetCreate, BudgetRead, BudgetUpdate
from app.models.settings.code_data import (
    CodeData,
    CodeDataCreate,
    CodeDataRead,
    CodeDataUpdate,
    CodeWithSubs,
)
from app.models.settings.credit_card import (
    CreditCard,
    CreditCardCreate,
    CreditCardRead,
    CreditCardUpdate,
)

__all__ = [
    "Account",
    "AccountCreate",
    "AccountRead",
    "AccountUpdate",
    "Alarm",
    "AlarmCreate",
    "AlarmRead",
    "AlarmUpdate",
    "Budget",
    "BudgetCreate",
    "BudgetRead",
    "BudgetUpdate",
    "CodeData",
    "CodeDataCreate",
    "CodeDataRead",
    "CodeDataUpdate",
    "CodeWithSubs",
    "CreditCard",
    "CreditCardCreate",
    "CreditCardRead",
    "CreditCardUpdate",
]
