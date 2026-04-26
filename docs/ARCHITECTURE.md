# 架构总览

## 高层资料流

```
┌─────────────────────┐
│  浏览器              │
│  (Streamlit Webview)│
└──────────┬──────────┘
           │ HTTP (form / button → rerun)
           ▼
┌─────────────────────────────────────────┐
│  Streamlit UI (Python)                  │
│  入口：main.py → main/main.py           │
│  ├─ main/ui/sidebar.py                  │
│  ├─ main/ui/tabs/{inventory, chests, …} │
│  └─ main/ui/api.py ──────────┐          │
└───────────────────────────────┼─────────┘
                                │ HTTP fetch (port 80 → /api/*)
                                ▼
┌─────────────────────────────────────────┐
│  Express + TypeScript API               │
│  /artifacts/api-server/src/             │
│  ├─ routes/bot.ts        (连线/聊天)    │
│  ├─ routes/snapshots.ts  (扫描/快照)    │
│  └─ routes/areas.ts      (区域 CRUD)    │
│  ├─ lib/bot.ts           (mineflayer)   │
│  ├─ lib/inventory.ts     (NBT 解析)     │
│  └─ lib/event-log.ts     (日志缓冲)     │
└─────────┬───────────────────┬───────────┘
          │ mineflayer        │ drizzle ORM
          ▼                   ▼
┌────────────────┐   ┌────────────────────┐
│  Minecraft     │   │  PostgreSQL        │
│  Server        │   │  - chest_areas     │
│                │   │  - container_      │
│                │   │    snapshots       │
│                │   │  - snapshot_items  │
│                │   │  - bot_state       │
└────────────────┘   └────────────────────┘
```

## 三层架构

### 1. 前端 — Streamlit (Python)

- **位置**：`main/`
- **入口**：根目录 `main.py` → 转给 `main/main.py:run()`
- **状态管理**：Streamlit 的 `session_state` 保存连线参数、auto-refresh 旗标
- **重新执行模式**：每次互动都会从头跑一次 `run()`，所以所有 IO 都尽量保持轻量

### 2. 后端 — Express + TypeScript

- **位置**：`artifacts/api-server/src/`
- **职责**：唯一负责 mineflayer 实例的程序；前端不可绕过它直接连 Minecraft
- **多机器人就绪**：`lib/bot.ts` 内部以 Map<string, BotInstance> 设计（目前只用一个 key），未来要扩成多机只需把 key 由 default 改成可变即可
- **NBT 解析**：`lib/inventory.ts` 使用 `prismarine-nbt` 解析潜影盒内的 `BlockEntityTag.Items`，把每颗潜影盒视为容器并自动展开内含物品

### 3. 共用资料库 — PostgreSQL + Drizzle

- **位置**：`lib/db/src/schema/inventory.ts`
- **指令**：`pnpm --filter @workspace/db run push` 同步 schema 到资料库

## 资料表

### `chest_areas`
| 栏位 | 型别 | 说明 |
|----|----|----|
| id | serial PK | |
| name | text NOT NULL | 区域显示名（例：主仓库） |
| description | text | 备注 |
| color | text | 显示色（预留） |
| vertex1 | text | 区域顶点 1，格式 `x,y,z` |
| vertex2 | text | 区域顶点 2，格式 `x,y,z` |
| extends_from | text | 上层区域名称（自由文字） |
| created_at | timestamptz | |

### `container_snapshots`
| 栏位 | 型别 | 说明 |
|----|----|----|
| id | serial PK | |
| taken_at | timestamptz | |
| source_type | text | `inventory` / `chest` |
| source_key | text | 唯一识别（背包：`inventory`；箱子：`dim:x,y,z`） |
| label | text | 自定标签 |
| dimension, x, y, z | nullable | 位置 |
| notes | text | 备注（如方块名） |
| area_id | int → chest_areas.id | ON DELETE SET NULL |

### `snapshot_items`
| 栏位 | 型别 | 说明 |
|----|----|----|
| id | serial PK | |
| snapshot_id | int → container_snapshots.id | ON DELETE CASCADE |
| item_name | text | minecraft id（如 `minecraft:diamond`） |
| display_name | text | 中文显示名 |
| count | int | |
| stack_size | int | 1 组的大小 |
| container | text | 容器路径，例：`主背包 → 紫色潜影盒#14` |
| is_shulker | bool | 这一笔是不是潜影盒本身（聚合时会被排除） |

### `bot_state`
单列表，存目前的连线状态快照，用于 `/api/bot/status`。

## 聚合规则（仓库总览）

`/api/inventory/aggregate` 的 SQL 概念：

1. 取每个 `source_key` 的**最新一笔**快照
2. 把这些快照的 `snapshot_items` 全部 UNION 起来
3. **排除 `is_shulker = true`**（避免重复计算潜影盒本身）
4. 按 `item_name` 聚合：sum(count)、保留 stack_size、记下 source_key 列表
5. 返回：种类数、总数、等效满箱数、每物品的箱-组-个

## 模组依赖关系（前端）

```
main.py (root shim)
  └─ main/main.py
       ├─ main/ui/styles.py
       ├─ main/ui/sidebar.py
       │    └─ main/ui/{api, format}
       ├─ main/ui/tabs/inventory.py
       │    └─ main/ui/{api, dialogs, icons}
       ├─ main/ui/tabs/chests.py
       │    └─ main/ui/{api, format, icons}
       ├─ main/ui/tabs/settings.py
       │    └─ main/ui/api
       ├─ main/ui/tabs/misc.py
       │    └─ main/ui/api
       └─ main/ui/tabs/logs.py
            └─ main/ui/api
```

## 关于 `artifacts/inventory-ui/app.py`

这个档案只是 **2 行薄壳**：把专案根加进 `sys.path`，呼叫 `main.main.run()`。  
存在原因是 Replit 平台的工作流绑定到这个路径。开发时改 `main/` 底下即可，不用动它。
