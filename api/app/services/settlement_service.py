"""Monthly settlement service (BE-019).

Snapshots every asset/liability net value for a vesting month. Per-asset-type
tables (Estate / Insurance / Loan / Stock) use single-month delete + reinsert.
AccountBalance and CreditCardBalance use CASCADE delete (``vesting_month >= target``)
to invalidate every later month's snapshot, preserving the legacy carry-forward
contract.

Wraps the 6 step calls in a SAVEPOINT (``session.begin_nested``). Any step
raising rolls back the entire settlement; the router maps that to HTTP 500.
"""
from __future__ import annotations

from sqlmodel import Session, delete, select

from app.models.assets.estate import Estate, EstateJournal
from app.models.assets.insurance import Insurance, InsuranceJournal
from app.models.assets.loan import Loan, LoanJournal
from app.models.assets.stock import StockDetail, StockJournal
from app.models.monthly_report.account_balance import AccountBalance
from app.models.monthly_report.credit_card_balance import CreditCardBalance
from app.models.monthly_report.estate_net_value_history import EstateNetValueHistory
from app.models.monthly_report.insurance_net_value_history import (
    InsuranceNetValueHistory,
)
from app.models.monthly_report.journal import Journal
from app.models.monthly_report.loan_balance import LoanBalance
from app.models.monthly_report.settlement import SettlementResult
from app.models.monthly_report.stock_net_value_history import StockNetValueHistory
from app.models.settings.account import Account
from app.models.settings.credit_card import CreditCard
from app.services.estate_value_service import select_month_market_value
from app.services.fx_lookup import BASE_CURRENCY, fx_rate_for_month
from app.services.insurance_value_service import select_month_surrender_value
from app.services.month_utils import month_end, previous_month
from app.services.stock_service import select_month_close_price


# ---------- Helpers ----------


def query_has_record_flags(session: Session, vesting_month: str) -> dict[str, bool]:
    """Whether the month has any Journal activity targeting each asset type."""
    flags = {"estate": False, "insurance": False, "loan": False, "stock": False}
    journals = session.exec(
        select(Journal).where(Journal.vesting_month == vesting_month)
    ).all()
    for j in journals:
        # Match action_main_type or action_sub_type or table reference.
        labels = {
            (j.action_main_type or "").lower(),
            (j.action_sub_type or "").lower(),
            (j.action_main_table or "").lower(),
            (j.action_sub_table or "").lower(),
        }
        if {"estate", "real_estate"} & labels:
            flags["estate"] = True
        if "insurance" in labels:
            flags["insurance"] = True
        if "loan" in labels or "liability" in labels:
            flags["loan"] = True
        if "stock" in labels:
            flags["stock"] = True
    return flags


# ---------- Per-asset-type steps ----------


def run_estate_step(session: Session, vesting_month: str) -> int:
    session.exec(
        delete(EstateNetValueHistory).where(
            EstateNetValueHistory.vesting_month == vesting_month
        )
    )
    estates = list(session.exec(select(Estate)).all())
    inserted = 0
    for estate in estates:
        cost_rows = session.exec(
            select(EstateJournal)
            .where(EstateJournal.estate_id == estate.estate_id)
            .where(EstateJournal.excute_date <= month_end(vesting_month))
        ).all()
        cost = sum(r.excute_price for r in cost_rows)
        # Prefer a user-recorded appraisal (估值) for the month; only fall back to
        # cost when none has been entered. This is what lets the property show
        # real appreciation instead of staying flat at purchase cost.
        logged = select_month_market_value(session, estate.estate_id, vesting_month)
        market_value = logged.market_value if logged is not None else cost
        # FX: estate carries its own currency (overseas property may be USD/JPY/...).
        fx_code = estate.fx_code or BASE_CURRENCY
        fx_rate = fx_rate_for_month(session, fx_code, vesting_month, on_missing="raise")
        session.add(
            EstateNetValueHistory(
                vesting_month=vesting_month,
                id=estate.estate_id,
                asset_id=estate.asset_id,
                name=estate.estate_name,
                market_value=round(market_value, 2),
                cost=round(cost, 2),
                estate_status=estate.estate_status,
                fx_code=fx_code,
                fx_rate=fx_rate,
            )
        )
        inserted += 1
    session.flush()
    return inserted


def run_insurance_step(session: Session, vesting_month: str) -> int:
    session.exec(
        delete(InsuranceNetValueHistory).where(
            InsuranceNetValueHistory.vesting_month == vesting_month
        )
    )
    policies = list(session.exec(select(Insurance)).all())
    inserted = 0
    for policy in policies:
        rows = session.exec(
            select(InsuranceJournal)
            .where(InsuranceJournal.insurance_id == policy.insurance_id)
            .where(InsuranceJournal.excute_date <= month_end(vesting_month))
        ).all()
        cost = 0.0
        surrender = 0.0
        for r in rows:
            if r.insurance_excute_type == "pay":        # 扣款 (premium payment)
                cost += r.excute_price
                surrender += r.excute_price
            elif r.insurance_excute_type == "cash":     # 配息 (dividend received)
                cost -= r.excute_price
            elif r.insurance_excute_type == "return":   # 贖回 (redemption)
                surrender -= r.excute_price
            # "expect" is legacy-only (migrated into Insurance_Value_History);
            # any straggler row is ignored here.
        # Prefer a user-recorded surrender value (解約金) for the month; only fall
        # back to the net-premium estimate when none has been entered. This is
        # what lets the policy show real cash-value growth instead of cost.
        logged = select_month_surrender_value(session, policy.insurance_id, vesting_month)
        if logged is not None:
            surrender = logged.surrender_value
        # FX: premium account drives currency; default base.
        account = session.exec(
            select(Account).where(Account.account_id == policy.in_account)
        ).first()
        fx_code = account.fx_code if account is not None else BASE_CURRENCY
        fx_rate = fx_rate_for_month(session, fx_code, vesting_month, on_missing="raise")
        session.add(
            InsuranceNetValueHistory(
                vesting_month=vesting_month,
                id=policy.insurance_id,
                asset_id=policy.asset_id,
                name=policy.insurance_name,
                surrender_value=round(surrender, 2),
                cost=round(cost, 2),
                fx_code=fx_code,
                fx_rate=fx_rate,
            )
        )
        inserted += 1
    session.flush()
    return inserted


def run_loan_step(session: Session, vesting_month: str) -> int:
    session.exec(
        delete(LoanBalance).where(LoanBalance.vesting_month == vesting_month)
    )
    loans = list(session.exec(select(Loan)).all())
    inserted = 0
    for loan in loans:
        rows = session.exec(
            select(LoanJournal)
            .where(LoanJournal.loan_id == loan.loan_id)
            .where(LoanJournal.excute_date <= month_end(vesting_month))
        ).all()
        principal = sum(
            r.excute_price for r in rows if r.loan_excute_type == "principal"
        )
        cost = sum(
            r.excute_price for r in rows if r.loan_excute_type in {"interest", "fee"}
        )
        balance = loan.amount - principal
        # FX: repayment account drives currency (overseas loan may be USD/JPY/...).
        account = session.exec(
            select(Account).where(Account.account_id == loan.account_id)
        ).first()
        fx_code = account.fx_code if account is not None else BASE_CURRENCY
        fx_rate = fx_rate_for_month(session, fx_code, vesting_month, on_missing="raise")
        session.add(
            LoanBalance(
                vesting_month=vesting_month,
                id=loan.loan_id,
                name=loan.loan_name,
                balance=round(balance, 2),
                cost=round(cost, 2),
                fx_code=fx_code,
                fx_rate=fx_rate,
            )
        )
        inserted += 1
    session.flush()
    return inserted


def run_stock_step(session: Session, vesting_month: str) -> int:
    session.exec(
        delete(StockNetValueHistory).where(
            StockNetValueHistory.vesting_month == vesting_month
        )
    )
    holdings = list(session.exec(select(StockJournal)).all())
    inserted = 0
    for h in holdings:
        rows = session.exec(
            select(StockDetail)
            .where(StockDetail.stock_id == h.stock_id)
            .where(StockDetail.excute_date <= month_end(vesting_month))
        ).all()
        # Driven by excute_type with abs() magnitudes (the write paths disagree on
        # the sign of amount), mirroring compute_stock_pnl_summary. ``excute_price``
        # is the whole-transaction cash amount, fees included — NOT a per-share
        # price — so cost sums those amounts directly (buys add, sells subtract);
        # it is not multiplied by the share count.
        buy_shares = sum(abs(r.excute_amount) for r in rows if r.excute_type in ("buy", "stock"))
        sell_shares = sum(abs(r.excute_amount) for r in rows if r.excute_type == "sell")
        buy_cost = sum(abs(r.excute_price) for r in rows if r.excute_type == "buy")
        sell_cost = sum(abs(r.excute_price) for r in rows if r.excute_type == "sell")
        amount = round(buy_shares, 6) - round(sell_shares, 6)
        if amount == 0:
            continue
        price_row = select_month_close_price(session, h.stock_code, vesting_month)
        close_price = price_row.close_price if price_row is not None else 0.0
        # Legacy ``price`` field semantically holds market value (close * amount).
        market_value = close_price * amount
        cost = buy_cost - sell_cost  # net cash invested in the remaining position
        # FX from settling account on the most-recent detail row, if any.
        last_detail = rows[-1] if rows else None
        fx_code = BASE_CURRENCY
        if last_detail is not None:
            account = session.exec(
                select(Account).where(Account.account_id == last_detail.account_id)
            ).first()
            if account is not None and account.fx_code:
                fx_code = account.fx_code
        fx_rate = fx_rate_for_month(session, fx_code, vesting_month, on_missing="raise")
        session.add(
            StockNetValueHistory(
                vesting_month=vesting_month,
                id=h.stock_id,
                asset_id=h.asset_id,
                stock_code=h.stock_code,
                stock_name=h.stock_name,
                amount=round(amount, 6),
                price=round(market_value, 2),
                cost=round(cost, 2),
                fx_code=fx_code,
                fx_rate=fx_rate,
            )
        )
        inserted += 1
    session.flush()
    return inserted


# ---------- AccountBalance / CreditCardBalance ----------


def run_account_balance_step(session: Session, vesting_month: str) -> int:
    """Cascade-delete from ``vesting_month`` onwards, then recompute the target month."""
    session.exec(
        delete(AccountBalance).where(AccountBalance.vesting_month >= vesting_month)
    )
    accounts = list(session.exec(select(Account)).all())
    journals = list(
        session.exec(
            select(Journal).where(Journal.vesting_month == vesting_month)
        ).all()
    )

    prev_month = previous_month(vesting_month)
    inserted = 0
    for account in accounts:
        prev = session.exec(
            select(AccountBalance)
            .where(AccountBalance.id == account.account_id)
            .where(AccountBalance.vesting_month == prev_month)
        ).first()
        balance = prev.balance if prev is not None else 0.0
        for j in journals:
            if (
                j.spend_way_table == "Account"
                and str(account.account_id) == str(j.spend_way)
            ):
                balance += j.spending
            if (
                j.action_sub_table == "Account"
                and str(account.account_id) == str(j.action_sub)
            ):
                if j.spend_way_type == "normal" and j.action_sub_type == "finance":
                    balance -= round(j.spending / float(j.note or 1), 2)
                elif j.spend_way_type == "finance" and j.action_sub_type == "normal":
                    balance -= round(j.spending * float(j.note or 1), 2)
                else:
                    balance -= j.spending
        balance = round(balance, 2)
        fx_rate = fx_rate_for_month(
            session, account.fx_code, vesting_month, on_missing="raise"
        )
        session.add(
            AccountBalance(
                vesting_month=vesting_month,
                id=account.account_id,
                name=account.name,
                balance=balance,
                fx_code=account.fx_code,
                fx_rate=fx_rate,
                is_calculate=account.is_calculate,
            )
        )
        inserted += 1
    session.flush()
    return inserted


def run_credit_card_balance_step(session: Session, vesting_month: str) -> int:
    session.exec(
        delete(CreditCardBalance).where(
            CreditCardBalance.vesting_month >= vesting_month
        )
    )
    cards = list(session.exec(select(CreditCard)).all())
    journals = list(
        session.exec(
            select(Journal).where(Journal.vesting_month == vesting_month)
        ).all()
    )
    prev_month = previous_month(vesting_month)
    inserted = 0
    for card in cards:
        prev = session.exec(
            select(CreditCardBalance)
            .where(CreditCardBalance.id == card.credit_card_id)
            .where(CreditCardBalance.vesting_month == prev_month)
        ).first()
        balance = prev.balance if prev is not None else 0.0
        for j in journals:
            if (
                j.spend_way_type == "credit_card"
                and str(j.spend_way) == str(card.credit_card_id)
            ):
                balance += j.spending
        balance = round(balance, 2)
        fx_rate = fx_rate_for_month(
            session, card.fx_code, vesting_month, on_missing="raise"
        )
        session.add(
            CreditCardBalance(
                vesting_month=vesting_month,
                id=card.credit_card_id,
                name=card.card_name,
                balance=balance,
                fx_rate=fx_rate,
            )
        )
        inserted += 1
    session.flush()
    return inserted


# ---------- Orchestrator ----------


def settle(session: Session, vesting_month: str) -> SettlementResult:
    """Run all settlement steps inside a SAVEPOINT.

    Per-asset steps gate on ``query_has_record_flags``. AccountBalance and
    CreditCardBalance always run. Any step raising rolls back the whole
    settlement.
    """
    flags = query_has_record_flags(session, vesting_month)
    estate_rows = insurance_rows = loan_rows = stock_rows = 0

    sp = session.begin_nested()
    try:
        if flags["estate"]:
            estate_rows = run_estate_step(session, vesting_month)
        if flags["insurance"]:
            insurance_rows = run_insurance_step(session, vesting_month)
        if flags["loan"]:
            loan_rows = run_loan_step(session, vesting_month)
        if flags["stock"]:
            stock_rows = run_stock_step(session, vesting_month)
        account_rows = run_account_balance_step(session, vesting_month)
        credit_card_rows = run_credit_card_balance_step(session, vesting_month)
        sp.commit()
    except Exception:
        sp.rollback()
        raise

    session.commit()
    return SettlementResult(
        vesting_month=vesting_month,
        estate_rows=estate_rows,
        insurance_rows=insurance_rows,
        loan_rows=loan_rows,
        stock_rows=stock_rows,
        account_rows=account_rows,
        credit_card_rows=credit_card_rows,
    )
