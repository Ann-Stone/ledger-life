# Ledger Life — Personal Finance Monorepo

A self-hosted personal-finance system: a Vue 3 SPA dashboard backed by a FastAPI accounting service. Tracks monthly cash flow, annual balance sheets, asset portfolios (stocks, real estate, insurance, loans), budgets, and reminders.

> No authentication. Single-user, single-machine by design.

🔗 **Demo**: [https://ann-stone.github.io/ledger-life/](https://ann-stone.github.io/ledger-life/)


## Layout

| Path     | Role                          | Stack                                                                |
|----------|-------------------------------|----------------------------------------------------------------------|
| [`view/`](view/) | Frontend SPA                  | Vue 3 + TypeScript, Pinia, Element Plus 2.x, Tailwind v4, ECharts, Vite 7 |
| [`api/`](api/)   | Backend REST API + SQLite     | FastAPI, SQLModel, Alembic, uv (Python 3.13)                          |
| `account-book-API/`, `account-book-view/` | Legacy reference code | Flask + Vue 2 — kept for migration reference only, not built or deployed. |

## Quickstart

Two terminals — backend first, then frontend:

```bash
# terminal 1 — backend on :9528
cd api
uv sync
uv run uvicorn app.main:app --reload --port 9528

# terminal 2 — frontend on :5173 (proxies /api → :9528)
cd view
pnpm install
pnpm dev
```

Open <http://127.0.0.1:5173>.

For UI-only work without a backend, use `pnpm dev:mock` in `view/` (MSW intercepts every API call).

Details:
- Frontend setup, env vars, build/type-check: [`view/README.md`](view/README.md)
- Backend architecture, routers, schemas: [`api/CLAUDE.md`](api/CLAUDE.md)
- Frontend architecture, store/component conventions: [`view/CLAUDE.md`](view/CLAUDE.md)
- Project-wide notes for AI assistants: [`CLAUDE.md`](CLAUDE.md)

## CI

GitHub Actions runs two jobs in parallel on every PR ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)):

- **`api`** — `uv sync` → `pytest --cov` → docs drift check
- **`view`** — `pnpm install --frozen-lockfile` → `type-check` → `build`

Both must pass before merge.

## Design system

Color tokens live in [`DESIGN.md`](DESIGN.md) (the WarmBalance Material Design 3 spec) and are wired into Tailwind via CSS custom properties in [`view/src/assets/main.css`](view/src/assets/main.css). For a static visual reference, open [`components.html`](components.html) directly in a browser.
