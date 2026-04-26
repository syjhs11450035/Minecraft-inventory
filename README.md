# 🤖 AI-Bot Minecraft 库存管理器

> 一个用 **mineflayer** 操控 Minecraft 机器人，并以 **Streamlit** 提供中文化 UI 的库存管理工具。  
> 机器人会以「外挂方式」开启箱子 / 木桶 / 末影箱，自动展开潜影盒，并把所有物品按 **箱-组-个** 的格式整理给你看。

![status](https://img.shields.io/badge/status-active-brightgreen)
![license](https://img.shields.io/badge/license-CC%20BY--NC--ND%204.0-lightgrey)
![python](https://img.shields.io/badge/python-3.11%2B-blue)
![node](https://img.shields.io/badge/node-20%2B-green)

---

## ✨ 特色

- 🤖 **真实 mineflayer 机器人** — 不是 mock，实际会上线、走路、开箱
- 📦 **潜影盒自动展开** — 透过 NBT 解析，潜影盒被视为 1 个箱子，但内容物会被算进总览
- 🧮 **箱-组-个换算** — 1 组 = 物品最大堆叠（石头 64、剑 1…），1 箱 = 27 组，自动算给你看
- 🗺️ **区域管理** — 把箱子按「主仓库 / 末影箱区 / 工业区…」分类，可设定顶点座标与上层区域
- 💾 **PostgreSQL 持久化** — 所有快照、区域设定都存进资料库，重启不丢
- 💬 **中文 UI** — Streamlit 写的控制台，深色侧栏 + 5 大分页

---

## 🏗️ 架构总览

<p align="center">
  <img src="docs/architecture.svg" alt="架构图" width="100%">
</p>

详细分层、资料流、表 schema 请见 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)。

---

## 🗂️ 专案目录

```
.
├── main.py                  # 根目录启动器（streamlit run main.py）
├── README.md
├── LICENSE                  # CC BY-NC-ND 4.0
├── replit.md                # Agent 工作记忆（开发用）
│
├── main/                    # ★ 所有自家程式都集中在这
│   ├── main.py              # 核心：组合 sidebar + 5 个 tabs
│   ├── ui/                  # Streamlit 前端模组
│   │   ├── api.py           #   API 客户端
│   │   ├── icons.py         #   物品 emoji 对照
│   │   ├── format.py        #   箱-组-个 换算
│   │   ├── styles.py        #   全域 CSS
│   │   ├── sidebar.py       #   左侧栏
│   │   ├── dialogs.py       #   扫描弹窗
│   │   └── tabs/            #   每个分页一个档案
│   │       ├── inventory.py
│   │       ├── chests.py
│   │       ├── settings.py
│   │       ├── misc.py
│   │       └── logs.py
│   └── js/
│       └── README.md        #   说明：JS 后端实际位置
│
├── docs/                    # 给开发者看的文件
│   ├── ARCHITECTURE.md
│   ├── PROGRESS.md
│   └── API.md
│
├── artifacts/               # Replit 平台绑定的工作区
│   ├── api-server/          #   Node 后端（pnpm workspace）
│   ├── inventory-ui/        #   Streamlit 工作流入口（薄壳）
│   └── mockup-sandbox/      #   元件预览（开发用）
│
└── lib/db/                  # 共用 PostgreSQL schema (drizzle)
```

---

## 🚀 快速开始

### 在 Replit 上

1. Fork 这个 repl
2. 等 PostgreSQL 自动建立完成
3. 三个工作流会自动起来：
   - `artifacts/api-server: API Server` — Node API
   - `artifacts/inventory-ui: Streamlit UI` — 中文控制台
   - `artifacts/mockup-sandbox: Component Preview Server` — 元件预览（可关）
4. 点开 Webview，进到 Streamlit UI，到「⚙️ 设定」分页填好你 Minecraft 伺服器的 IP / 名称，按【💾 储存设定】
5. 回侧栏按【🚀 连线】

### 本地开发

```bash
# 1. 装相依
pnpm install                    # Node / TypeScript
uv sync  # 或 pip install -e .  # Python

# 2. 设定环境变数
export DATABASE_URL="postgres://user:pass@localhost:5432/mc_inv"

# 3. 推送 DB schema
pnpm --filter @workspace/db run push

# 4. 启动 API 后端
pnpm --filter @workspace/api-server run dev

# 5. 另开终端机启动 UI
streamlit run main.py
```

---

## 📐 核心概念：箱 - 组 - 个

<p align="center">
  <img src="docs/box-stack-math.svg" alt="箱-组-个 换算" width="100%">
</p>

| 单位 | 定义 |
|----|------|
| **1 个** | 最小单位 — 一颗物品 |
| **1 组 (stack)** | 物品的最大堆叠数。石头 = 64、末影珍珠 = 16、剑 = 1，由 minecraft-data 自动取得 |
| **1 箱 (box)** | 固定 = **27 组**（一个潜影盒大小） |

数量会自动换算成「`X 箱 - Y 组 - Z 个`」。  
例如：石头 4096 → `2 箱 - 10 组 - 0 个`。

---

## 📄 授权

本专案以 **[CC BY-NC-ND 4.0](LICENSE)** 授权释出：

- ✓ 你可以自由**浏览、下载、分享**原始档案
- ✗ **不可商业用途**（NC）
- ✗ **不可修改后再发布**（ND）
- ※ 散布时必须**保留作者署名**与本授权连结

完整条款见 [LICENSE](LICENSE)。

---

## 🗒️ 更新记录

请见 [`docs/PROGRESS.md`](docs/PROGRESS.md)。
