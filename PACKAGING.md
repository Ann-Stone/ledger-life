# Packaging — Framework Decision (NOT YET ACTIVE)

> ## STOP — DO NOT IMPLEMENT YET
>
> **This document records a framework decision only. No packaging work
> should be executed until ALL of the following are true:**
>
> 1. **Data-cleaning phase** is complete and merged on `main`.
> 2. **UX optimization phase** is complete and merged on `main`.
> 3. `POST_FRONTEND_TODO.md` §2 (the 8 schema-divergence rows) is fully
>    resolved — every row marked `keep` or `migrate`, and any required
>    Alembic migration shipped. Migrations baked into a packaged binary
>    are immutable for end-users, so this is a hard gate.
>
> If you are an AI session reading this during the data-cleaning or UX
> phase: **do not create a PyInstaller spec, do not add `pywebview`,
> do not modify `view/vite.config.ts` `base`, do not mount static files
> in `api/app/main.py`**. The only legitimate cross-references during
> those phases are the "What the data-cleaning phase should pick up for
> free" and "What the UX phase should pick up for free" sections below
> — those are guidance for the *current* phase, not invitations to
> start packaging work.

---

## Context

Networth is a "Single-user, single-machine by design" app
(see [`README.md`](README.md)). After the monorepo refactor finishes
(data cleaning + UX polish), the app will be packaged so non-technical
friends can run it locally — no `pnpm`, `uv`, Python, or Docker on
their machine. This file locks in the packaging approach now so the
remaining refactor work can leave the right hooks in place.

### User decisions (do not relitigate)

- **Target audience**: non-technical friends. Double-click to launch.
- **Plan depth**: selection + framework only. Implementation deferred.
- **Data boundary**: friends receive an empty DB plus an optional
  sample-data load. The developer's personal
  `~/.networth/networth.db` never ships.

## Recommendation — PyInstaller + pywebview

A single executable per OS that:

1. Spawns embedded `uvicorn` on a random localhost port (not 9528 —
   avoid clash with dev installs).
2. Serves the pre-built Vue SPA (`view/dist/`) as `StaticFiles` mounted
   on the same FastAPI app. One origin, no CORS / proxy in production.
3. Opens a native window via `pywebview` pointed at
   `http://127.0.0.1:<port>/`. No browser tab, no terminal.
4. On first launch, runs Alembic `upgrade head` in-process to create
   `~/.networth/networth.db`. Offers an optional sample-data load.

### Why this over alternatives

| Option | Verdict | Reason |
|--------|---------|--------|
| **PyInstaller + pywebview** *(picked)* | ✅ | All-Python stack matches the repo. One binary per OS. ~80–150 MB (pandas/yfinance dominate). Native window UX. |
| Tauri (Rust + WebView + Python sidecar) | ❌ | Still needs PyInstaller for the Python sidecar — gains a Rust toolchain dependency without removing the Python bundling problem. |
| Electron + Python sidecar | ❌ | +150 MB Chromium baseline on top of the Python bundle. Overkill. |
| PyInstaller + system browser | ⚠️ Fallback | Simpler, but "browser tab pops up" confuses non-technical users. Reserve in case `pywebview` blocks us on Apple Silicon. |
| Docker Compose | ❌ | Ruled out — friends don't run Docker. |

## Framework constraints to surface now

These are **observations**, not action items for the current phase:

- [`api/app/main.py`](api/app/main.py) — will need to conditionally
  mount `view/dist/` as `StaticFiles` when an env var (e.g.
  `NETWORTH_BUNDLED=1`) is set. Routers stay under `/api/...`;
  SPA history-mode fallback serves `index.html`.
- [`view/vite.config.ts:10`](view/vite.config.ts) — `base: '/networth/'`
  is the GitHub Pages base. The bundled build needs `base: '/'` (or env-
  driven).
- [`api/app/config.py:17`](api/app/config.py) — `database_url` default
  (`sqlite:///~/.networth/networth.db`) is already correct for bundled
  mode. No change needed; confirmed.
- Alembic — bundled launcher needs in-process
  `alembic.command.upgrade(config, "head")`. PyInstaller's `--add-data`
  flag ships `alembic.ini` + `migrations/`.
- [`api/pyproject.toml`](api/pyproject.toml) — `yfinance` + `pandas`
  are heavy. Before packaging, audit whether both are used by
  production code paths or only by scripts; if scripts-only, move to a
  dev/scripts group.

## What the data-cleaning phase should pick up for free

These are appropriate to handle **during** data cleaning. They are not
packaging implementation — they are pre-conditions:

1. **Empty-DB first-launch verification** —
   `create_db_and_tables()` ([`api/app/database.py:49`](api/app/database.py))
   already runs on lifespan startup. **Verify**: launch with
   `DATABASE_URL=sqlite:////tmp/test_fresh.db uv run dev` and confirm
   all routers respond without 500s.
2. **Sample-data path** — extend (or fork)
   [`api/scripts/seed_dev_data.py`](api/scripts/seed_dev_data.py) into
   a `seed_sample_data` callable. Sample data must be synthetic.
3. **Resolve `POST_FRONTEND_TODO.md` §2** — hard gate for packaging.
4. **Skip private config defaults** — keep
   [`api/config/invoice_skip.json`](api/config/invoice_skip.json) and
   `merchant_mapping.json` as empty defaults. The Taiwan-specific
   values in `POST_FRONTEND_TODO.md` §5 are personal config and must
   not ship in the public package.
5. **Logs path** — in bundled mode logs should land in
   `~/.networth/logs/` (next to the DB), not the gitignored
   `api/logs/` which assumes a writable CWD.

## What the UX phase should pick up for free

1. **First-launch dialog** — a single Vue view shown when the DB has
   zero rows in `Account`. Two buttons: "Start fresh" / "Load sample
   data".
2. **Window chrome assets** — `.icns` / `.ico` / `.png` icon set under
   `view/public/` or a new `packaging/assets/` directory.
3. **External-link audit** — review any `target="_blank"` /
   `window.open` in `view/src/` for behavior inside a `pywebview`
   window (it shells out to the system browser, which is fine but
   worth confirming).

## Open decisions (defer, but flagged)

- **macOS code signing / notarization** — Apple Developer Program
  ($99/yr) or accept right-click → Open friction. Decide before first
  macOS release.
- **Windows SmartScreen** — same problem class. Code-signing cert or
  tolerate the "Unknown publisher" dialog.
- **Auto-update** — out of scope for v1. Friends re-download manually.
- **`yfinance` network access** — packaged app makes outbound HTTPS
  calls for stock prices. Document this in the end-user README so
  friends aren't surprised by firewall prompts.

## Verification (only when packaging implementation begins)

1. From a fresh user profile / VM with no `~/.networth/`, launch the
   binary. Confirm the window opens, the DB is created at
   `~/.networth/networth.db`, and the dashboard loads without errors.
2. Click "Load sample data" and confirm at least one record shows in
   each major view (Cash Flow, Balance Sheet, Other Assets).
3. Close and re-open the app; confirm data persists.
4. macOS: `codesign -dv` the `.app`; `spctl --assess` for Gatekeeper.
   Windows: confirm the `.exe` launches on a machine that has never
   had Python installed.
5. Confirm no developer-personal data leaked into the bundle:
   `strings` the binary for `agentstone`, the developer's email, and
   any account names from the developer's real DB.

## Out of scope for this document

- The PyInstaller spec file.
- The `pywebview` launcher script.
- The Vite production-build env-var wiring.
- The first-launch Vue dialog implementation.
- Any release / CI / signing pipeline.

All of the above happen in a **future implementation phase**, after
the three gates at the top of this file are satisfied.
