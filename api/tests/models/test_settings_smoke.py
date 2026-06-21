"""Round-trip smoke test for the Settings domain tables."""
from __future__ import annotations

from sqlmodel import Session, select

from app.models.settings import (
    Account,
    Alarm,
    Budget,
    CodeData,
    CreditCard,
)


def test_settings_models_roundtrip(session: Session) -> None:
    # CodeData first, because Budget FK-references it.
    code = CodeData(
        code_id="INC01",
        code_type="income",
        name="Salary",
        parent_id=None,
        in_use="Y",
        code_index=1,
    )
    account = Account(
        account_id="BANK-CHASE-01",
        name="Chase Checking",
        account_type="bank",
        fx_code="USD",
        is_calculate="Y",
        in_use="Y",
        discount=1.0,
        memo="Primary checking",
        owner="stone",
        account_index=1,
    )
    budget = Budget(
        budget_year="2026",
        category_code="INC01",
        category_name="Salary",
        code_type="income",
        expected01=100000.0,
        expected02=100000.0,
        expected03=100000.0,
        expected04=100000.0,
        expected05=100000.0,
        expected06=100000.0,
        expected07=100000.0,
        expected08=100000.0,
        expected09=100000.0,
        expected10=100000.0,
        expected11=100000.0,
        expected12=200000.0,
    )
    credit = CreditCard(
        credit_card_id="CC-VISA-01",
        card_name="Chase Sapphire",
        card_no="4111-XXXX-XXXX-1111",
        last_day=25,
        charge_day=15,
        limit_date=20,
        feedback_way="cashback",
        fx_code="USD",
        in_use="Y",
        credit_card_index=1,
        note="Primary card",
    )
    alarm = Alarm(
        alarm_type="credit-card-charge",
        alarm_date="20260115",
        content="Chase Sapphire autopay",
        due_date="20260120",
    )

    session.add_all([code, account, budget, credit, alarm])
    session.commit()

    got_account = session.exec(select(Account).where(Account.account_id == "BANK-CHASE-01")).one()
    assert got_account.id is not None
    assert got_account.name == "Chase Checking"

    got_code = session.exec(select(CodeData).where(CodeData.code_id == "INC01")).one()
    assert got_code.name == "Salary"

    got_budget = session.exec(
        select(Budget).where(Budget.budget_year == "2026", Budget.category_code == "INC01")
    ).one()
    assert got_budget.expected12 == 200000.0

    got_credit = session.exec(
        select(CreditCard).where(CreditCard.credit_card_id == "CC-VISA-01")
    ).one()
    assert got_credit.card_name == "Chase Sapphire"

    got_alarm = session.exec(select(Alarm)).one()
    assert got_alarm.alarm_id is not None
    assert got_alarm.content == "Chase Sapphire autopay"
