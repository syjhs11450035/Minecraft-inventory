# 开发进度 / Changelog

> 时间格式：YYYY-MM-DD（项目时区为 UTC）

## 进行中

- [ ] AI 自动整理（设定页已预留 toggle 与 API key 栏位，但功能尚未实作）
- [ ] 多机器人扩展（后端 Map 已就绪，前端尚未提供 bot 切换 UI）

## 2026-04-25

### 重构：所有自家程式集中到 `main/`
- 新增 `main/main.py`、`main/ui/{api,icons,format,styles,sidebar,dialogs}.py`
- 五个分页拆成独立档：`main/ui/tabs/{inventory,chests,settings,misc,logs}.py`
- 根目录 `main.py` 与 `artifacts/inventory-ui/app.py` 改成薄壳（仅 sys.path + run()）
- 新增 `docs/`（ARCHITECTURE / PROGRESS / API）与根 `README.md`
- 加入 `LICENSE` (CC BY-NC-ND 4.0)

### UI 改版
- 移除 H1 大标题，每个分页也不显示标题
- 仓库分页改成左右两栏：左 = 表格（图片 / 名称 / 箱 / 组 / 个），右 = 操作 + 统计卡
- 新增「🧰 其他」分页，把指令送出表单移过去（原本在侧栏）
- 自动刷新切换搬到「⚙️ 设定」分页
- 模式列表移除「自动整理（开发中）」选项
- 区域管理新增三个栏位：**顶点 1 / 顶点 2 / 延伸于**

### 后端
- `chest_areas` 资料表新增 `vertex1`、`vertex2`、`extends_from` 三栏
- `/api/areas` (POST/PATCH) 接受新栏位
- `/api/areas` (GET) 在回应中带回新栏位与 `snapshotCount`

## 2026-04-24

### 区域功能 v1
- 新增 `chest_areas` 资料表
- 新增 `/api/areas` 路由（GET/POST/PATCH/DELETE）
- 在 `container_snapshots` 加上 `area_id` 外键（ON DELETE SET NULL）
- 「箱子管理」分页：区域 CRUD（data_editor + 新增 / 删除按钮）
- 扫描背包 / 扫描附近箱子时使用 `@st.dialog` 弹出对话框选择区域

### UI 模板化
- 深色侧栏 + 4 大分页结构（📦/🗺️/⚙️/📊）
- 状态徽章（已上线 / 连线中 / 错误 / 已离线）
- 物品 emoji 图标对照表（约 100+ 项）
- 统计卡片（物品种类 / 物品总数 / 等效满箱）

## 2026-04-23

### 后端基础
- mineflayer 机器人管理器（连线 / 离线 / 聊天 / 移动 / 开箱）
- 物品解析器（含潜影盒 NBT 自动展开为容器）
- PostgreSQL schema（drizzle）
- 快照 API 与聚合 API（`/api/snapshots*`、`/api/inventory/aggregate`）
- 事件日志缓冲（`/api/bot/logs`）
