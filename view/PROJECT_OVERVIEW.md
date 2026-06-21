# Balance Sheet View — Architecture & Conventions

> Single source of truth for frontend conventions. `view/AGENTS.md`, `view/CLAUDE.md`, `view/GEMINI.md` all delegate here. `view/AGENTS.md` additionally holds QA checklists.

---

## Architecture Principles

### 1. Composition API only
`<script setup lang="ts">`. No Options API. No `defineComponent()`.

### 2. Pinia stores — flat, domain-scoped
Each business domain has exactly one store. **No store imports another store.** Mutate state via actions, never directly from components.

### 3. API layer separation
All HTTP goes through `src/api/`. Components and stores **never call `axios` directly** — use the wrapper in `src/utils/request.ts`.

### 4. Types — single source of truth
All data models live in `src/types/models.ts`. **No inline interface definitions anywhere else.**

### 5. Tailwind for layout, Element Plus for interaction
- Tailwind: layout, spacing, grid, color, typography utilities.
- Element Plus: Table, Form, Dialog, DatePicker, Select, Tabs, Pagination, Notification.
- Theme customization: CSS variables in `src/assets/main.css` `:root {}` block **only**.
- **Never fight Element Plus styles with Tailwind `!important`**.

### 6. Component responsibility boundaries
- `src/components/charts/` — **stateless**, props in only.
- `src/components/ui/`, `src/components/layout/` — reusable primitives.
- `src/views/*View.vue` — **own state** (subscribe to stores, pass data down).
- Sub-components scoped to a single view live under `src/views/<Name>/`.

### 7. Naming
- Vue files: `PascalCase.vue`
- TypeScript files: `camelCase.ts`
- Views: suffix `View` (e.g., `DashboardView.vue`)
- Stores: `use` + noun + `Store` (e.g., `useAppStore`)
- Composables: `use` + verb/noun
- API functions: verb + noun (e.g., `getBalanceSheet`, `createAccount`)

---

## DO / DO NOT

### DO
- Use the `<MoneyDisplay>` component for all money values (formats via `Intl.NumberFormat`).
- Use `<el-message>` / `<el-notification>` for user feedback — never `alert()`.
- Run `pnpm type-check` before submitting a PR.

### DO NOT
- Inline TypeScript interfaces — always reference `src/types/models.ts`.
- Call `axios` directly — always go through `src/utils/request.ts`.
- Create new files in `src/stores/`, `src/router/`, or `src/api/` outside the task's stated scope.
- Change mock data unless the task explicitly requires it.

---

## Environment & Commands

```env
VITE_API_BASE_URL=/api          # proxied to localhost:9528 in dev
VITE_USE_MOCK=false             # true for GitHub Pages mock mode
```

```bash
pnpm dev          # http://127.0.0.1:5173
pnpm build        # production build
pnpm build:mock   # GitHub Pages build with mock data
pnpm type-check   # must pass before any PR
```

---

## GitHub Pages Mock Strategy

When `VITE_USE_MOCK=true`:
- MSW intercepts all `/api/*` requests in the browser.
- Mock handlers: `src/api/mock/handlers.ts`.
- Mock data: `src/api/mock/data/*.json`.

---

## Common Pitfalls

| Problem | Fix |
|---------|-----|
| Reactive data not updating | Check Pinia state — mutate via actions, not directly. |
| `ref` vs `reactive` confusion | `ref()` for primitives, `reactive()` for objects. |
| Element Plus table blank | `el-table-column` `prop` must match data key; `:data` must be an array. |
| ECharts blank on first render | Container needs explicit width/height; use the `autoresize` prop. |
| Tailwind class ignored | Tailwind v4 has no preflight — don't expect CSS resets. |
| Element Plus style override | Use CSS variables in `:root {}`, not Tailwind on `<el-*>`. |
| TypeScript error after data shape change | Update `src/types/models.ts` first, then mock data. |
