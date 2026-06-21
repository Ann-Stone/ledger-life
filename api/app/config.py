from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables and .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        extra="ignore",
    )

    app_name: str = "Networth API"
    debug: bool = True
    port: int = 9528
    database_url: str = "sqlite:///~/.networth/networth.db"
    # Run the FX/stock month-end backfill on startup (disabled in tests).
    enable_startup_catch_up: bool = True

    # Telegram bookkeeping bot (optional). Names follow the secrets-config
    # formula <SERVICE>_<KEY>; values live in .env (Tier 0), never in the repo.
    # Keep TELEGRAM_BOT_ENABLED=false on the dev machine so the reload server
    # never opens a second getUpdates poller against the always-on instance
    # (Telegram allows exactly one poller per token — a second one 409s).
    telegram_bot_enabled: bool = False
    telegram_bot_token: str = ""
    telegram_allowed_chat_id: int = 0

    invoice_card_no: str = ""
    invoice_password: str = ""
    invoice_app_id: str = ""
    invoice_skip_path: str = "config/invoice_skip.json"
    merchant_mapping_path: str = "config/merchant_mapping.json"
    invoice_error_log: str = "logs/invoice_import_errors.log"


settings = Settings()
