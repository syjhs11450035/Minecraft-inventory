# Workspace

## Overview

Minecraft AI bot inventory manager. A mineflayer-based bot connects to a Minecraft server, opens chests / barrels / ender chests, parses any shulker boxes inside, and stores everything in PostgreSQL. A Streamlit web UI (Simplified Chinese) shows the aggregated total in **箱 - 组 - 个** (boxes / stacks / individual items) format.

## Architecture

- **`artifacts/api-server`** — Express 5 + mineflayer backend. Manages a single bot instance, exposes REST endpoints under `/api/bot/...` and `/api/snapshots/...`. Future-ready for multi-bot expansion.
- **`artifacts/inventory-ui`** — Python Streamlit frontend served at `/`. Talks to the API via `http://localhost:80/api`.
- **`lib/db`** — Drizzle schema for `container_snapshots` and `snapshot_items`.
- **`lib/api-zod`, `lib/api-spec`, `lib/api-client-react`** — present from scaffold; not yet wired (the Streamlit client uses raw `requests`).

## Stack

- **Bot**: mineflayer + minecraft-data + prismarine-nbt
- **API**: Express 5 + Drizzle ORM + Zod
- **DB**: PostgreSQL
- **UI**: Python 3.11 + Streamlit + pandas + requests
- **Monorepo**: pnpm workspaces

## Key API endpoints

- `GET  /api/bot/status` — connection state
- `POST /api/bot/connect` — `{host, port, username, version?, auth?}`
- `POST /api/bot/disconnect`
- `POST /api/bot/chat` — `{message}`
- `GET  /api/bot/nearby-chest?range=6`
- `GET  /api/bot/inventory-preview` — current inventory (no save)
- `POST /api/snapshots/inventory` — snapshot bot inventory + nested shulker contents
- `POST /api/snapshots/chest` — open nearest container, snapshot contents (incl. shulker contents)
- `GET  /api/snapshots`, `GET /api/snapshots/:id`, `DELETE /api/snapshots/:id`
- `GET  /api/inventory/aggregate` — totals per item across the latest snapshot of each location, returned with `boxes / stacks / singles` breakdown

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
