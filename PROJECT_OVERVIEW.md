# Balance Sheet — Project Overview

> Single source of truth for monorepo-wide rules. Root `AGENTS.md` and root
> `CLAUDE.md` both delegate here. For per-subproject conventions, see
> `view/PROJECT_OVERVIEW.md` and `api/PROJECT_OVERVIEW.md` (the per-subproject
> `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` all delegate to those).

---

## Monorepo Structure

- `view/` — frontend SPA (Vue 3 + TS).
- `api/` — backend API (FastAPI + SQLModel + SQLite).
- `account-book-API/`, `account-book-view/` — legacy code, reference only.

> **Packaging note**: [`PACKAGING.md`](PACKAGING.md) records the chosen
> packaging approach (PyInstaller + pywebview) for distributing the app
> to non-technical friends. **Do not implement any of it** until data
> cleaning + UX optimization are merged and `POST_FRONTEND_TODO.md` §2
> is resolved. The file's top banner enumerates the gates.

## Subproject Routing Guide

When analyzing an issue, mark the scope in the output tag:

- **Frontend-only** → `[DONE:view]`
- **Backend-only** → `[DONE:api]`
- **Full-stack** → `[DONE:view,api]` (auto-split into two sub-issues)
- **Monorepo-level** (CI/CD, shared configs, docs) → `[DONE]`

## Database access policy (privacy)

Do **not** read row-level data from any SQLite database in this workspace. Covers `~/.networth/networth.db`, `account-book-API/data/ledger.db`, any `*.db` / `*.db-journal` / `*.db-wal` / `*.db-shm` file. Prohibited unless the user explicitly authorises the specific file in the current session:

- `sqlite3 <db> "SELECT ..."` / `.dump` / `.schema` / interactive shell on a real DB
- `cat`, `xxd`, `hexdump`, `strings`, `Read` tool, or any other read on a `.db` blob
- Python / Node scripts that connect to the DB and emit row contents
- `git show` / `git log -p` on committed `.db` blobs
- Running `api/scripts/migrate_from_legacy.py` or `api/scripts/seed_dev_data.py` against the user's real DB without explicit permission

If you need to confirm data state, **provide the SQL to the user** and ask them to paste back the result. Example: *"Please run `sqlite3 ~/.networth/networth.db \"SELECT COUNT(*) FROM Code_Data WHERE code_type='Passive';\"` and share the output."*

Schema-only questions: read `account-book-API/data/create_db.sql` or the SQLModel classes under `api/app/models/`. Exempt from the rule: test fixtures the AI itself builds (e.g. `api/tests/fixtures/build_legacy_tiny.py`), `sqlite://` in-memory test engines, static JSON under `view/src/api/mock/data/`.

## Subproject conventions

- Frontend: see **[view/PROJECT_OVERVIEW.md](view/PROJECT_OVERVIEW.md)**.
- Backend: see **[api/PROJECT_OVERVIEW.md](api/PROJECT_OVERVIEW.md)**.

QA checklists (per-feature business rules + edge cases) live in `view/AGENTS.md` and `api/AGENTS.md`.
