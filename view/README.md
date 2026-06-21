# Balance Sheet — Frontend (`view/`)

Personal finance dashboard SPA: monthly cash flow, annual balance sheet, asset management (stocks, real estate, insurance, loans), budgets, reminders.

> Sibling backend lives at [`../api/`](../api/). For monorepo overview see the [root README](../README.md).

---

## Requirements

| Tool   | Version       | Notes                                                                                     |
|--------|---------------|-------------------------------------------------------------------------------------------|
| Node   | **22 LTS**    | Vite 8 requires ≥ 20.19; CI pins 22. No `.nvmrc` is checked in — match this README.       |
| pnpm   | **9.15+**     | `packageManager` field in `package.json` pins the version. Install via `corepack enable` or `npm install -g pnpm@9`. |

## Install

```bash
cd view
pnpm install
```

## Environment

Copy the example file and edit if needed:

```bash
cp .env.example .env
```

| Variable             | Default | Meaning                                                                                                                 |
|----------------------|---------|-------------------------------------------------------------------------------------------------------------------------|
| `VITE_API_BASE_URL`  | `/api`  | Path prefix used by `src/utils/request.ts`. In dev, Vite proxies `/api/*` → `http://localhost:9528` (strips the prefix). |
| `VITE_USE_MOCK`      | `false` | When `true`, MSW intercepts every `/api/*` request in the browser using fixtures under `src/api/mock/`. No backend needed. |

`.env.production` sets `VITE_USE_MOCK=true` for the GitHub Pages bundle (so the deployed demo works without a server).

## Dev modes

### Against the real backend

```bash
pnpm dev
```

- Dev server: <http://127.0.0.1:5173>
- Requires the FastAPI backend running on `:9528` — see [`../api/CLAUDE.md`](../api/CLAUDE.md) for backend startup.
- Vite proxy config: see [`vite.config.ts`](vite.config.ts).

### Standalone (MSW mock)

```bash
pnpm dev:mock
```

- Same dev server, but with `VITE_USE_MOCK=true` — no backend required.
- Useful for UI work, contract previews, GitHub Pages dry-runs.

## Build & quality gates

| Command                | What it does                                                                          |
|------------------------|---------------------------------------------------------------------------------------|
| `pnpm type-check`   | `vue-tsc --build --force` — full TS pass. **Must be green before any PR.**            |
| `pnpm build`        | `vue-tsc -b && vite build` → `dist/`. Production bundle hitting the real API.         |
| `pnpm build:mock`   | Same as `build` but with `VITE_USE_MOCK=true` → GitHub Pages bundle with MSW baked in.|
| `pnpm preview`      | Serves the last `build` output locally for smoke-checking.                            |

`pnpm type-check` and `pnpm build` also run in CI on every PR touching `view/**` — see [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

## Architecture quick reference

See [`view/CLAUDE.md`](CLAUDE.md) for the full breakdown. Key conventions:

- **Composition API only** (`<script setup lang="ts">`)
- **Pinia stores** — one per domain, flat, never imported by each other
- **All HTTP through `src/api/`** — `src/utils/request.ts` is the only axios touchpoint
- **All types in `src/types/models.ts`** — no inline interface declarations elsewhere
- **Tailwind for layout, Element Plus for interaction** — design tokens in `src/assets/main.css`

## Troubleshooting

- **`type-check` fails after a pull**: run `pnpm install` first; new types from upstream may not be in your `node_modules`.
- **Dev server returns 502/connect ECONNREFUSED**: backend isn't on `:9528`. Either start the API or use `pnpm dev:mock`.
- **Build:mock fails with MSW worker error**: ensure `public/mockServiceWorker.js` exists (regenerate with `npx msw init public --save` if missing).
