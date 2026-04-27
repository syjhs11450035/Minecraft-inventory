# Workspace

## Overview

Minecraft AI bot inventory manager. A mineflayer-based bot connects to a Minecraft server, opens chests / barrels / ender chests, parses any shulker boxes inside, and stores everything in PostgreSQL. A Streamlit web UI (Simplified Chinese) shows the aggregated total in **箱 - 组 - 个** (boxes / stacks / individual items) format.

## Architecture

- **`/main/`** — All first-party Python code. `main/main.py` is the entry; `main/ui/{api,icons,format,styles,sidebar,dialogs}.py` are shared helpers; `main/ui/tabs/{inventory,chests,settings,misc,logs}.py` is one file per tab.
- **`/main.py`** (root) — thin shim that adds project root to sys.path then calls `main.main.run()`. The Streamlit workflow runs from project root via this entry.
- **`artifacts/inventory-ui/app.py`** — alternative thin shim that re-exports `main.main.run()`. Currently the workflow runs `main.py` from the project root.
- **`artifacts/api-server`** — Express 5 + mineflayer backend. Routes: `bot.ts`, `snapshots.ts`, `areas.ts`, `health.ts`. Lib: `bot.ts`, `inventory.ts`, `event-log.ts`. Bundled with esbuild → `dist/index.mjs`.
- **`lib/db`** — Drizzle schema for `chest_areas`, `container_snapshots`, `snapshot_items`, `bot_state`. Push schema with `pnpm --filter @workspace/db run push`.
- **`docs/`** — `ARCHITECTURE.md`, `PROGRESS.md`, `API.md` (for GitHub readers).

## Stack

- **Bot**: mineflayer + minecraft-data + prismarine-nbt
- **API**: Express 5 + Drizzle ORM + Zod
- **DB**: PostgreSQL (Replit-managed, via `DATABASE_URL`)
- **UI**: Python 3.11 + Streamlit + pandas + requests (managed by `uv`)
- **Monorepo**: pnpm workspaces

## Routing (path-based via Replit proxy)

- `/`     → Streamlit UI (port 5000) — artifact `inventory-ui`
- `/api`  → Express API (port 8080) — artifact `api-server`
- `/__mockup` → Vite design canvas (port 8081) — artifact `mockup-sandbox` (unused)

## Key API endpoints

See `docs/API.md` for the full reference. Summary:

- `GET  /api/bot/status`, `POST /api/bot/connect|disconnect|chat`, `GET|DELETE /api/bot/logs`
- `POST /api/snapshots/inventory|chest` (both accept `{label, areaId}`)
- `GET  /api/snapshots`, `GET|DELETE /api/snapshots/:id`
- `GET  /api/inventory/aggregate` — boxes / stacks / singles
- `GET|POST|PATCH|DELETE /api/areas` — chest area CRUD with `name, description, vertex1, vertex2, extendsFrom`

## Box / Stack / Single math

- 1 stack (组) = item's `stackSize` from minecraft-data (default 64)
- 1 box (箱) = 27 stacks (a shulker box has 27 slots)
- The `/inventory/aggregate` endpoint returns these pre-computed for each item

## Key Commands

- `pnpm run typecheck` — typecheck all packages
- `pnpm --filter @workspace/db run push` — push DB schema changes
- `pnpm --filter @workspace/api-server run dev` — run API server (also handled by workflow)
- `uv sync` — install / sync Python dependencies

## Roadmap (open items from `docs/PROGRESS.md`)

- AI 自动整理（设定页已预留 toggle 与 API key 栏位，但功能尚未实作）
- 多机器人扩展（后端 Map 已就绪，前端尚未提供 bot 切换 UI）
