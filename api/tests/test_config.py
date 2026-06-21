"""Tests for app.config.Settings."""
from __future__ import annotations

import importlib
from pathlib import Path

import pytest


def _fresh_settings_cls():
    """Reload app.config to get a fresh Settings class bound to current env."""
    import app.config as cfg

    importlib.reload(cfg)
    return cfg


def test_settings_defaults(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Default values are applied when no env or .env is present."""
    # Isolate from any ambient env vars / .env files.
    for key in [
        "APP_NAME",
        "DEBUG",
        "PORT",
        "DATABASE_URL",
        "INVOICE_CARD_NO",
        "INVOICE_PASSWORD",
        "INVOICE_APP_ID",
        "INVOICE_SKIP_PATH",
        "MERCHANT_MAPPING_PATH",
        "IMPORT_CSV",
    ]:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.chdir(tmp_path)

    cfg = _fresh_settings_cls()
    s = cfg.Settings()

    assert s.app_name == "Networth API"
    assert s.debug is True
    assert s.port == 9528
    assert s.database_url == "sqlite:///~/.networth/networth.db"


def test_invoice_fields_default_empty(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    for key in [
        "INVOICE_CARD_NO",
        "INVOICE_PASSWORD",
        "INVOICE_APP_ID",
    ]:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.chdir(tmp_path)

    cfg = _fresh_settings_cls()
    s = cfg.Settings()

    assert s.invoice_card_no == ""
    assert s.invoice_password == ""
    assert s.invoice_app_id == ""
    assert s.invoice_skip_path == "config/invoice_skip.json"
    assert s.merchant_mapping_path == "config/merchant_mapping.json"


def test_import_config_fields(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Import-related config fields default to expected values."""
    for key in [
        "INVOICE_SKIP_PATH",
        "MERCHANT_MAPPING_PATH",
        "INVOICE_ERROR_LOG",
    ]:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.chdir(tmp_path)

    cfg = _fresh_settings_cls()
    s = cfg.Settings()

    assert s.invoice_skip_path == "config/invoice_skip.json"
    assert s.merchant_mapping_path == "config/merchant_mapping.json"
    assert s.invoice_error_log == "logs/invoice_import_errors.log"


def test_settings_singleton_import() -> None:
    """`settings` singleton is importable from app.config."""
    from app.config import Settings, settings

    assert isinstance(settings, Settings)


def test_env_file_overrides_defaults(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A local .env is read when Settings() is constructed."""
    for key in ["DEBUG", "DATABASE_URL"]:
        monkeypatch.delenv(key, raising=False)
    (tmp_path / ".env").write_text(
        "DEBUG=false\nDATABASE_URL=sqlite:///tmp/x.db\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    cfg = _fresh_settings_cls()
    s = cfg.Settings()

    assert s.debug is False
    assert s.database_url == "sqlite:///tmp/x.db"


def test_env_var_overrides_defaults(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Environment variables override Settings defaults."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///tmp/z.db")

    cfg = _fresh_settings_cls()
    s = cfg.Settings()

    assert s.database_url == "sqlite:///tmp/z.db"
