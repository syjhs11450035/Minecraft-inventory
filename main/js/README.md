# `main/js` — Node / TypeScript 后端

> 此资料夹仅作**说明导引**用。真正的 Node 后端程式码位于  
> [`/artifacts/api-server/`](../../artifacts/api-server/)
>
> 因为这个专案是 **pnpm monorepo**，后端套件由 `pnpm-workspace.yaml`
> 与 `package.json` 透过 `@workspace/api-server` 名称参照，
> 不能任意搬动到非 `artifacts/` 路径下，否则会破坏建置流程。

## 后端档案地图

```
artifacts/api-server/src/
├── index.ts              # Express 入口
├── lib/
│   ├── bot.ts            # mineflayer 机器人封装（连线/离线/聊天/开箱…）
│   ├── inventory.ts      # 物品解析 + 潜影盒 NBT 自动展开
│   └── event-log.ts      # 环形日志缓冲（给 /api/bot/logs 使用）
└── routes/
    ├── index.ts          # 路由汇总
    ├── health.ts         # /api/healthz
    ├── bot.ts            # /api/bot/status, /connect, /disconnect, /chat, /logs
    ├── snapshots.ts      # /api/snapshots*, /api/inventory/aggregate
    └── areas.ts          # /api/areas（CRUD）
```

## 共用资料库 schema

PostgreSQL schema 由 Drizzle ORM 管理，定义在  
[`lib/db/src/schema/inventory.ts`](../../lib/db/src/schema/inventory.ts)，  
透过 `pnpm --filter @workspace/db run push` 同步到资料库。

## 启动指令

```bash
# API 服务（开发模式，热重载）
pnpm --filter @workspace/api-server run dev

# 推送 schema 变更
pnpm --filter @workspace/db run push
```

## API 完整对照

请见 [`docs/API.md`](../../docs/API.md)
