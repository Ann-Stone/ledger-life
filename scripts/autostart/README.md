# Auto-start: Networth API + Telegram bookkeeping bot (macOS / Windows / Linux)

The API server embeds a Telegram bot for real-time bookkeeping. Record entries
from Telegram — no browser, no public URL (the bot uses long polling, so nothing
is exposed to the internet). The frontend stays on-demand; it is NOT needed for
bookkeeping.

**The bot is OS-agnostic.** It is embedded in the API's startup, so it runs
wherever the API runs — macOS, Windows, or Linux — with no platform-specific
code. There is nothing to "start the Windows way" vs "the Mac way" in the app
itself. The only per-OS part is *auto-start at boot*, and that is delegated to
**schedctl**: one manifest (`api/schedule.toml`) renders the correct artifact for
the host (launchd agent on macOS, Task Scheduler job on Windows). `schedctl
doctor` also catches the Telegram "one poller per token" (409) collision up front.

---

## A. Run it now for testing — any OS, no schedctl

The fastest way to try the bot. Auto-start is not involved.

1. **Create the bot** — message **@BotFather** → `/newbot` → copy the **token**;
   message **@userinfobot** → copy your numeric **chat id**.
2. **`api/.env`** (copy from `.env.example`):
   ```
   TELEGRAM_BOT_ENABLED=true
   TELEGRAM_BOT_TOKEN=<token>
   TELEGRAM_ALLOWED_CHAT_ID=<your chat id>
   ```
3. From `api/`: `uv run uvicorn app.main:app --host 127.0.0.1 --port 9528`
   (avoid `uv run dev` if anything else is polling the same token — one poller
   per token).
4. In Telegram, send `120 午餐` → 支出 → pick a category → pick an account → ✅ 確認.
   Expect `✅ 已記錄 #<id>`.

This works identically on macOS, Windows, and Linux — so you can fully test on
your Mac today.

---

## B. Auto-start at login/boot — schedctl (cross-platform)

The **same** `api/schedule.toml` is used on every OS; schedctl renders the right
backend for the host.

1. **Install schedctl** and verify the backend it picked:
   - macOS:   `brew install Ann-Stone/tap/schedctl`
   - Windows: `scoop install schedctl`
   - `schedctl version`  → e.g. `schedctl 0.1.0 (darwin/arm64, backend: launchd)`
2. **`uv sync`** in `api/` (once).
3. **`api/.env`** as in section A, plus the DB path for your OS:
   - macOS / Linux: `DATABASE_URL=sqlite:///~/.networth/networth.db`
   - Windows:       `DATABASE_URL=sqlite:///C:/Users/<you>/.networth/networth.db`
   `.env` is git-ignored — never commit the token (secrets-config Tier-0).
4. **Point the manifest at this host** — edit `working_dir` in
   `api/schedule.toml` to the absolute path of your `api/` directory
   (macOS `/Users/<you>/.../networth/api`, Windows `C:\Users\<you>\networth\api`).
   Ensure `uv` is on the job's PATH, or use the absolute `uv` path in `command` /
   add an `[env] PATH = "..."` line.
5. **Install + verify** (run from `api/`):
   ```
   schedctl install --manifest schedule.toml
   schedctl doctor                 # MUST pass — catches 409 poller + port clashes
   schedctl status com.networth.api
   ```
6. **Verify** — reboot or log out/in; the bot responds in Telegram with no manual
   start. Test as in A4.

---

## Day-to-day

- Update/remove: re-run `schedctl install` after editing the manifest, or
  `schedctl uninstall com.networth.api` to remove the job.
- Logs: `api/logs/networth-api.{out,err}.log`.
- To view the dashboard, start the frontend separately when you want it.

## Gotchas

- **One poller per token.** Telegram allows exactly one `getUpdates` poller per
  bot token. Keep `TELEGRAM_BOT_ENABLED=false` on every host except the one
  designated always-on instance, so a second process never opens a competing
  poller. `schedctl doctor` fails if two `poll` jobs share a token — fix the
  config, do not force it.
- **Register a new secret** (the secrets-config flow): add the key to
  `api/.env.example` → set the real value in `api/.env` → reference it by name in
  `app/config.py` → it is loaded at runtime via the manifest's `env_file`.
