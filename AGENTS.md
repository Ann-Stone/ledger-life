# Balance Sheet — Project Root

Monorepo-wide rules live in **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** — read that file before doing anything. It is the single source of truth for project structure, subproject routing, the database access policy, and the frontend / backend overviews.

Subproject-specific details cascade automatically: when working inside `view/` or `api/`, the per-directory `CLAUDE.md` (architecture / conventions) and `AGENTS.md` (QA strategy / checklists) are loaded on top of this root context.
