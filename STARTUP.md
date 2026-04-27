# 啟動說明

> 本專案是一個 **monorepo**，包含三個獨立服務，全部由 pnpm workspace 與 uv 管理。
> 設定值（連線參數、AI 開關、HTTP 伺服器…）統一儲存在 `data/settings.json`，**只要設一次就會記住**。

---

## 0. 環境需求

| 項目 | 版本 | 安裝方式 |
| --- | --- | --- |
| Node.js | ≥ 20 | Replit Nix 已預裝 |
| pnpm | ≥ 10 | `npm i -g pnpm` 或 corepack |
| Python | 3.11 | Replit Nix 已預裝 |
| uv | latest | `curl -Ls https://astral.sh/uv/install.sh \| sh` |
| PostgreSQL | 16+ | Replit 已自動建立，並注入 `DATABASE_URL` |

> 在 Replit 環境中以上都已就緒，不需手動安裝。

---

## 1. 初次設定（只要做一次）

```bash
# 安裝 Node 依賴（含 mineflayer / express / anthropic SDK）
pnpm install

# 安裝 Python 依賴（streamlit / pandas / requests）
uv sync

# 把資料表建到 PostgreSQL
pnpm --filter @workspace/db run push
```

> 若 schema 有衝突，可改用 `pnpm --filter @workspace/db run push-force`（會重寫表）。

---

## 2. 三個服務的啟動指令

每個服務都對應一個 Replit Workflow，平台會自動啟動；
**手動執行**（例如本機開發）的指令如下：

### 2-A. 後台 API + Mineflayer 機器人（Node / TypeScript）

```bash
pnpm --filter @workspace/api-server run dev
```

* 監聽 `PORT`（Replit 自動分配 → 透過反向代理對外暴露為 `/api`）
* 內含：
  * `/api/bot/*` — 機器人連線、狀態、聊天、附近箱子搜尋
  * `/api/snapshots/*` — 容器掃描快照（背包 / 箱子 → 寫入 DB）
  * `/api/chest/preview` — 箱子預覽（不入庫；優先用 `/data get block`）
  * `/api/areas` — 區域 CRUD
  * `/api/settings` — **持久化設定**（讀寫 `data/settings.json`）
  * `/api/ai/history` — AI 對話歷史

### 2-B. Streamlit UI（Python）

```bash
uv run streamlit run main.py \
  --server.port 5000 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false
```

* 進入點：根目錄的 `main.py`（薄殼）→ `main/py/main.py`（實作）
* 開啟瀏覽器後會看到「倉庫 / 箱子管理 / 設定 / 其他 / 日誌」五個分頁
* 啟動時會 **自動從 `/api/settings` 載入設定**，並把上次「啟用」的 HTTP 靜態伺服器一併帶起來

### 2-C. 內建 HTTP 靜態伺服器（serving `/html/`）

由 Streamlit 程序內的執行緒提供：

* 在「設定」分頁的「🌍 內建 HTTP 靜態伺服器」面板按 **▶️ 啟動**
* 啟動後設定會存進 JSON，下次 Streamlit 啟動會自動接著開
* 預設 port `8000`，可在介面修改

> 也可以用 Python 內建的 `http.server` 取代：`uv run python -m http.server 8000 -d html`

### 2-D. （可選）設計用的 Mockup Sandbox

```bash
pnpm --filter @workspace/mockup-sandbox run dev
```

對應 `/__mockup` 路徑；目前專案沒在用，預設不啟動。

---

## 3. 設定檔結構

設定統一在 `data/settings.json`：

```json
{
  "connection": {
    "host": "localhost",
    "port": 25565,
    "username": "InvBot",
    "version": "",
    "auth": "offline"
  },
  "ai": {
    "enabled": false,
    "model": "claude-sonnet-4-6",
    "systemPrompt": "你是一個 Minecraft 機器人助手……",
    "replyInChat": true
  },
  "htmlServer": {
    "enabled": false,
    "port": 8000
  },
  "ui": {
    "autoRefresh": false
  }
}
```

* 由 API 服務啟動時自動建立，預設值寫在 `artifacts/api-server/src/lib/settings.ts`
* 修改方式：
  1. **介面修改（推薦）** — Streamlit 的「設定」分頁所有面板都是即時存檔
  2. **REST API** — `PATCH /api/settings`（body 採 deep merge）
  3. **手改 JSON** — 改完後呼叫 `POST /api/settings/reload` 或重啟 API 服務

---

## 4. 環境變數

| 變數 | 必填 | 說明 |
| --- | --- | --- |
| `DATABASE_URL` | ✅ | PostgreSQL 連線字串（Replit 自動注入） |
| `PORT` | ✅ | API 伺服器監聽埠（Replit 自動指定） |
| `SETTINGS_PATH` | 選 | 自訂設定檔位置（預設 `data/settings.json`） |
| `API_BASE` | 選 | Streamlit 用來打 API 的基底 URL（預設 `http://localhost:80/api`） |
| `AI_INTEGRATIONS_ANTHROPIC_BASE_URL` | AI 才需要 | 由 Replit AI 整合自動設定 |
| `AI_INTEGRATIONS_ANTHROPIC_API_KEY` | AI 才需要 | 由 Replit AI 整合自動設定 |
| `SESSION_SECRET` | 選 | 為將來擴充預留 |

---

## 5. 常用工作流檢查

```bash
# 健康檢查
curl http://localhost:80/api/healthz

# 看目前設定（會建立預設 JSON 檔）
curl http://localhost:80/api/settings

# 讓機器人連線（用設定裡的參數）
curl -X POST http://localhost:80/api/bot/connect \
     -H "Content-Type: application/json" \
     -d '{"host":"my.server.tw","port":25565,"username":"InvBot"}'

# 預覽附近箱子（不寫 DB）
curl -X POST http://localhost:80/api/chest/preview \
     -H "Content-Type: application/json" \
     -d '{"range":6}'

# 啟用 AI
curl -X PATCH http://localhost:80/api/settings \
     -H "Content-Type: application/json" \
     -d '{"ai":{"enabled":true}}'
```

---

## 6. 部署建議

* **Reserved VM** — 推薦：機器人會持續維持 TCP 連線，autoscale 會把它殺掉
* **Autoscale** — 不適合，會冷啟動讓 mineflayer 斷線
* **靜態網站** — 不適用

部署目標：`minecaibot--syjhs11450035.replit.app`
（在 Replit 介面點 Deploy → 選 Reserved VM 即可）
