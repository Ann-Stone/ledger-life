"""Policy matrix for the shared FX lookup.

Settlement uses ``on_missing="raise"`` (missing rate must abort the whole
settlement); reports use the default ``"fallback"`` (degrade to 1.0).
"""
import pytest
from sqlmodel import Session

from app.models.dashboard.fx_rate import FXRate
from app.services.fx_lookup import fx_rate_for_month

VM = "202604"


def test_base_currency_is_one_under_both_policies(session: Session) -> None:
    assert fx_rate_for_month(session, "TWD", VM) == 1.0
    assert fx_rate_for_month(session, "TWD", VM, on_missing="raise") == 1.0


def test_falsy_currency_split(session: Session) -> None:
    # Reports short-circuit falsy currency to 1.0; settlement treats it as
    # an unknown currency and raises.
    assert fx_rate_for_month(session, None, VM) == 1.0
    assert fx_rate_for_month(session, "", VM) == 1.0
    with pytest.raises(ValueError):
        fx_rate_for_month(session, None, VM, on_missing="raise")


def test_no_rows_at_all(session: Session) -> None:
    assert fx_rate_for_month(session, "USD", VM) == 1.0
    with pytest.raises(ValueError):
        fx_rate_for_month(session, "USD", VM, on_missing="raise")


def test_window_then_prior_row_fallback(session: Session) -> None:
    # Only a row after the window → both policies fall back to it.
    session.add(FXRate(import_date="20270101", code="USD", buy_rate=33.0))
    session.commit()
    assert fx_rate_for_month(session, "USD", VM) == 33.0
    assert fx_rate_for_month(session, "USD", VM, on_missing="raise") == 33.0
    # A row inside the window wins over the out-of-window fallback.
    session.add(FXRate(import_date="20260415", code="USD", buy_rate=31.5))
    session.commit()
    assert fx_rate_for_month(session, "USD", VM) == 31.5
    assert fx_rate_for_month(session, "USD", VM, on_missing="raise") == 31.5


def test_latest_in_window_wins(session: Session) -> None:
    session.add(FXRate(import_date="20260401", code="USD", buy_rate=30.0))
    session.add(FXRate(import_date="20260420", code="USD", buy_rate=32.0))
    session.commit()
    assert fx_rate_for_month(session, "USD", VM) == 32.0
