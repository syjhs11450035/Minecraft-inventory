# Workspace

## Quick Access

- **快速查看**: https://88258c72-76c6-49a1-87fb-de8030c96b06-00-h5dfpgzc98cc.riker.replit.dev/

## Overview

Minecraft AI bot inventory manager. A mineflayer-based bot connects to a Minecraft server, opens chests / barrels / ender chests, parses any shulker boxes inside, and stores everything in PostgreSQL. A Streamlit web UI (Simplified Chinese) shows the aggregated total in **箱 - 组 - 个** (boxes / stacks / individual items) format.

## Architecture

- **`/main/`** — ★ All first-party Python code lives here, organised by user preference.
  - `main/main.py` — entry: page config, sidebar, 5 tabs router
  - `main/ui/{api,icons,format,styles,sidebar,dialogs}.py` — shared UI helpers
  - `main/ui/tabs/{inventory,chests,settings,misc,logs}.py` — one file per tab
  - `main/js/README.md` — pointer doc (real JS is in `artifacts/api-server/src/`, can't move due to pnpm workspace)
- **`/main.py`** (root) — thin shim: adds project root to sys.path → `main.main.run()`. Lets you run `streamlit run main.py` from project root.
- **`artifacts/api-server`** — Express 5 + mineflayer backend. Routes split: `bot.ts`, `snapshots.ts`, `areas.ts`, `health.ts`. Lib: `bot.ts`, `inventory.ts`, `event-log.ts`.
- **`artifacts/inventory-ui/app.py`** — thin shim required by Replit workflow binding. Just `from main.main import run; run()` after sys.path fix.
- **`lib/db`** — Drizzle schema for `chest_areas`, `container_snapshots`, `snapshot_items`, `bot_state`.
- **`docs/`** — ARCHITECTURE.md / PROGRESS.md / API.md (for GitHub readers).
- **`README.md`** + **`LICENSE`** (CC BY-NC-ND 4.0) at root for GitHub presentation.

## Stack

- **Bot**: mineflayer + minecraft-data + prismarine-nbt
- **API**: Express 5 + Drizzle ORM + Zod
- **DB**: PostgreSQL
- **UI**: Python 3.11 + Streamlit + pandas + requests
- **Monorepo**: pnpm workspaces

## Key API endpoints

See `docs/API.md` for the full reference. Quick summary:

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
- `pnpm --filter @workspace/api-server run dev` — run API server

## Workflows

- `artifacts/api-server: API Server` — Express on port 8080, exposed at `/api`
- `artifacts/inventory-ui: Streamlit UI` — Streamlit on port 5000, exposed at `/`
- `artifacts/mockup-sandbox: Component Preview Server` — design canvas (unused)
