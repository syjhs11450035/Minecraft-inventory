# API 参考

API 基底位址：`http://<host>/api`  
所有请求 / 回应都是 JSON，错误以 `{"error": "..."}` 形式返回。

---

## 健康检查

### `GET /healthz`
```json
{ "status": "ok" }
```

---

## 机器人控制

### `GET /bot/status`
返回当前机器人状态。
```json
{
  "status": "spawned" | "connecting" | "connected" | "disconnected" | "error",
  "message": "...",
  "host": "localhost",
  "port": 25565,
  "username": "InvBot",
  "version": "1.20.4",
  "position": { "dimension": "overworld", "x": 0, "y": 64, "z": 0 },
  "health": 20,
  "food": 20
}
```

### `POST /bot/connect`
请求：
```json
{
  "host": "localhost",
  "port": 25565,
  "username": "InvBot",
  "version": "1.20.4",   // 选填，留空自动侦测
  "auth": "offline"      // "offline" | "microsoft"
}
```
回应：`{ "ok": true }` 或 `{ "error": "..." }`

### `POST /bot/disconnect`
让机器人离线。`{ "ok": true }`

### `POST /bot/chat`
```json
{ "message": "/home" }
```

### `GET /bot/logs?limit=200`
返回环形缓冲内的事件日志（最多 200 笔）。
```json
{
  "entries": [
    { "ts": 1714000000000, "level": "info" | "warn" | "error" | "chat" | "system",
      "message": "..." }
  ]
}
```

### `DELETE /bot/logs`
清空日志缓冲。

---

## 区域管理

### `GET /areas`
```json
{
  "areas": [
    {
      "id": 1,
      "name": "主仓库",
      "description": "主要存放区",
      "color": null,
      "vertex1": "100,64,200",
      "vertex2": "120,68,220",
      "extendsFrom": null,
      "createdAt": "2026-04-25 08:54:02+00",
      "snapshotCount": 12
    }
  ]
}
```

### `POST /areas`
```json
{
  "name": "主仓库",
  "description": "主要存放区",   // 选填
  "color": "#3b82f6",            // 选填
  "vertex1": "100,64,200",       // 选填
  "vertex2": "120,68,220",       // 选填
  "extendsFrom": "外部仓库"      // 选填
}
```
回应：`{ "ok": true, "area": {...} }`

### `PATCH /areas/:id`
任意子集合的区域栏位即可更新。

### `DELETE /areas/:id`
删除区域。区域内的快照会被把 `area_id` 设为 NULL（不会一起删）。

---

## 快照

### `POST /snapshots/inventory`
扫描机器人背包（**机器人需在线**）。
```json
{
  "label": "主背包",     // 选填
  "areaId": 1            // 选填，null = 未分类
}
```
回应：
```json
{
  "ok": true,
  "snapshotId": 42,
  "itemCount": 17
}
```

### `POST /snapshots/chest`
扫描附近的箱子 / 木桶 / 末影箱。
```json
{
  "label": "矿石箱",
  "range": 6,            // 1-32 格，预设 6
  "areaId": 1            // 选填
}
```
回应：
```json
{
  "ok": true,
  "snapshotId": 43,
  "itemCount": 8,
  "target": { "name": "chest", "x": 100, "y": 64, "z": 200 }
}
```

### `GET /snapshots`
最近 200 笔快照。
```json
{
  "snapshots": [
    {
      "id": 42,
      "takenAt": "2026-04-25T08:54:02",
      "sourceType": "inventory",
      "sourceKey": "inventory",
      "label": "主背包",
      "dimension": "overworld",
      "x": null, "y": null, "z": null,
      "notes": null,
      "areaId": 1,
      "areaName": "主仓库"
    }
  ]
}
```

### `GET /snapshots/:id`
单一快照含所有物品明细。
```json
{
  "snapshot": { ...同上单笔... },
  "items": [
    {
      "itemName": "diamond",
      "displayName": "钻石",
      "count": 4096,
      "stackSize": 64,
      "container": "主背包 → 紫色潜影盒#14",
      "isShulker": false
    }
  ]
}
```

### `DELETE /snapshots/:id`
连同其 `snapshot_items` 一起删除。

---

## 仓库总览（聚合）

### `GET /inventory/aggregate`
跨所有快照（每个 source_key 取最新一笔），按物品聚合。**排除潜影盒本身**，只算内容物。
```json
{
  "items": [
    {
      "itemName": "diamond",
      "displayName": "钻石",
      "stackSize": 64,
      "total": 4096,
      "boxes": 2,
      "stacks": 10,
      "singles": 0,
      "sourceKey": "overworld:100,64,200"   // 主要来源（最近的）
    }
  ]
}
```

---

## 错误回应

所有错误一律以 HTTP 4xx/5xx + 以下格式返回：
```json
{ "error": "机器人未上线" }
```
