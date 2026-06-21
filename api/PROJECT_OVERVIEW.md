# Networth API — Architecture & Conventions

> Single source of truth for backend conventions. `api/AGENTS.md`, `api/CLAUDE.md`, `api/GEMINI.md` all delegate here. `api/AGENTS.md` additionally holds QA checklists.

---

## Architecture Principles

### 1. Three layers: Router → Service → Model
- **Routers** handle HTTP (request parsing, response formatting, status codes).
- **Services** hold business logic (calculations, cross-domain queries, transformations).
- **Models** are SQLModel table definitions + Create/Update/Read schemas, co-located in `app/models/<domain>/`.

> The legacy `Initial_Setting` table is intentionally not ported (orphan in legacy `account_balance_model.py`; initialization code already commented out).

### 2. Services are flat functions
Plain functions in `app/services/`. **No classes.** `session: Session` is the first parameter, never stored on a class or module global. Cross-domain services import models from multiple domains directly.

### 3. Database session via `Depends(get_session)`
All routers receive `session` via FastAPI dependency injection. **Never create sessions manually in routers.** Look at any existing router for the pattern.

### 4. Unified response envelope
All endpoints return `ApiResponse[T]` on success, `ApiError` on failure. Both live in `app/schemas/response.py` — the only file in `schemas/`.

### 5. BackgroundTasks open their own Session
Stock price / FX rate / invoice CSV imports run as FastAPI `BackgroundTasks`. They **must** open `with Session(engine) as s:` inside the task — the request session is closed by the time they run.

---

## DO / DO NOT

### DO
- Return `ApiResponse(data=result)` from every endpoint.
- Pass `session` as the first parameter to all service functions.
- Define Create/Update/Read schemas in the same file as the table model.
- Use `select()` from SQLModel — never raw SQL.
- Run `uv run alembic revision --autogenerate -m "..."` after any model change.
- Use `X | None = None` (not `Optional[X]`).

### DO NOT
- Import `Session` or create sessions inside routers.
- Put business logic in routers — delegate to `services/`.
- Create new files in `app/schemas/` — only `response.py` lives there.
- Import one service from another service.
- Hardcode config values — use `from app.config import settings`.

---

## Naming Conventions

| What | Convention | Example |
|------|-----------|---------|
| Python files | snake_case | `account.py`, `code_data.py` |
| Model classes | PascalCase | `Account`, `CodeData`, `StockJournal` |
| Schema classes | Model + suffix | `AccountCreate`, `AccountUpdate`, `AccountRead` |
| Router files | plural noun | `accounts.py`, `codes.py`, `journals.py` |
| Service files | `<domain>_service` | `setting_service.py`, `settlement_service.py` |
| Functions | verb_noun | `get_accounts()`, `create_journal()`, `settle_month()` |
| URL paths | kebab-case | `/settings/credit-cards`, `/monthly-report/journals` |

---

## Commands

```bash
uv run dev                                    # start uvicorn on port 9528
uv run alembic revision --autogenerate -m ""  # generate migration after model change
uv run alembic upgrade head                   # apply migrations
uv run pytest                                 # gate: coverage ≥ 70%
uv run export-docs                            # regenerate api/docs/ split spec
uv run export-docs --check                    # CI drift check
```

Two `scripts/` entry-points carry their own usage docs in their module docstring:
- `seed_dev_data.py` — dev seed loader (refuses production-pattern URLs).
- `migrate_from_legacy.py` — BE-005 one-shot legacy → new schema migrator.

Production DB lives at `~/.networth/networth.db` (overridable via `DATABASE_URL`). `api/` must never contain `*.db` files — `.gitignore` enforces this.

---

## API documentation discipline (contract-as-spec)

The Swagger UI at `/docs` and the committed split spec under `api/docs/api-reference.md`, `api/docs/api-reference/`, and `api/docs/openapi/` **are the API spec** consumed by the frontend refactor. Non-negotiable; enforced in BE-032 by `uv run export-docs --check`.

### Every endpoint MUST
- Have `summary=` and `description=` on the route decorator (English).
- Use Pydantic models for both request and response (never raw `dict`).
- Declare `responses={...}` with error-code examples.
- Annotate query params: `Annotated[T, Query(..., description="...", examples=[...])]`.

### Every Pydantic field MUST
- Use `Field(..., description="...", examples=[...])`.
- Add `model_config = ConfigDict(json_schema_extra={"example": {...}})` to every schema class for a full-model example.

### Contract boundary
Frontend agents start at `api/docs/api-reference.md` and follow the table to `api-reference/<domain>/<sub-router>.md`. Drill-down is `openapi/<domain>/<sub-router>.json` plus the per-schema files listed in `x-schema-files`. Frontend agents **do not** read `api/app/routers/**` or `api/app/models/**` — if the spec is missing something, fix the spec.

### Language
All ticket content, OpenAPI text, code comments, and generated docs are in **English**. User-facing conversation uses Traditional Chinese only.

---

## Common Pitfalls

| Problem | Fix |
|---------|-----|
| BackgroundTask DB error | Open `with Session(engine) as s:` inside the task; never reuse the request session. |
| Alembic doesn't see new model | Re-export it through `app/models/<domain>/__init__.py` so `app/models/__init__.py` picks it up. |
| Composite PK not working | Use `__table_args__ = (PrimaryKeyConstraint("col1", "col2"),)`. |
| Pydantic v1 patterns sneaking in | `.from_orm()` → `model_validate()`; `Optional[X]` → `X | None`. |
| Date string format mismatch | Store as `YYYYMMDD` / `YYYYMM` string (model contract); parse legacy via `dateutil.parser.parse(...).strftime(...)`. |
| Session closed after yield | Never store session references outside `Depends` scope. |
