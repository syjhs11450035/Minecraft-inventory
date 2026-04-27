# Workspace

## Overview

Minecraft AI bot inventory manager. A mineflayer-based bot connects to a Minecraft server, opens chests / barrels / ender chests, parses any shulker boxes inside, and stores everything in PostgreSQL. A Streamlit web UI (Simplified Chinese) shows the aggregated total in **箱 - 组 - 个** (boxes / stacks / individual items) format. Includes an `ai!`-prefixed AI chat handler (Anthropic via Replit AI Integration) and a `/data get block`–based chest preview that works without physically opening the container.

## Directory layout

```
/main
  /py        ← all first-party Python (Streamlit UI, helpers)
    main.py
    /ui      ← shared modules + tabs/{inventory,chests,settings,misc,logs}.py
  /js        ← symlink → ../artifacts/api-server/src  (pnpm workspace constraint)
  /server    ← optional built-in HTTP static server for /html (toggled from settings)
/html        ← static site served by /main/server when enabled
/artifacts
  /api-server      ← Express + mineflayer
  /inventory-ui    ← Streamlit shell (re-imports from main/py/main.py)
  /mockup-sandbox  ← unused vite design canvas
/lib/db      ← Drizzle schema (chest_areas, container_snapshots, snapshot_items, bot_state)
/main.py     ← root shim → from main.py.main import run; run()
```

## Stack

- **Bot**: mineflayer + minecraft-data + prismarine-nbt
- **API**: Express 5 + Drizzle ORM + Zod + Anthropic SDK (Replit AI Integration)
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
- `POST /api/chest/preview {x,y,z,range}` — read chest contents without writing to DB; tries `/data get block` first (needs OP), then falls back to a brief openContainer
- `GET  /api/snapshots`, `GET|DELETE /api/snapshots/:id`
- `GET  /api/inventory/aggregate`
- `GET|POST|PATCH|DELETE /api/areas`
- `GET|PATCH /api/settings` — runtime config (currently AI block: `enabled, model, systemPrompt, replyInChat`)
- `GET|DELETE /api/ai/history` — sliding-window AI chat history (in memory, max 12)

## AI handler (`ai!` prefix)

When AI is enabled in `/api/settings`, the bot listens for chat lines matching `<player> ai!<prompt>` (or `ai!<prompt>` from console). The reply is generated via Anthropic and posted back to chat as `@player <reply>`. Simple keyword-driven actions are also recognized in the reply (`跟我來` → look at sender, `跳` → jump once, `停下` → clear control states).

Anthropic credentials are auto-provisioned via `setupReplitAIIntegrations` and exposed as `AI_INTEGRATIONS_ANTHROPIC_BASE_URL` / `AI_INTEGRATIONS_ANTHROPIC_API_KEY`. No user-managed key is required.

## Box / Stack / Single math

- 1 stack (组) = item's `stackSize` from minecraft-data (default 64)
- 1 box (箱) = 27 stacks (a shulker box has 27 slots)

## Key Commands

- `pnpm run typecheck` — typecheck all packages
- `pnpm --filter @workspace/db run push` — push DB schema changes
- `pnpm --filter @workspace/api-server run dev` — run API server (also handled by workflow)
- `uv sync` — install / sync Python dependencies

## Deployment notes

For mineflayer-based bots, **Reserved VM** is the right deployment shape: an autoscale deployment will kill the bot whenever the HTTP server idles, breaking the persistent Minecraft connection. The Streamlit UI is fine on autoscale, but for a single combined deployment Reserved VM is recommended.
