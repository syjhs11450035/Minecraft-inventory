import os
import time
from typing import Any

import pandas as pd
import requests
import streamlit as st

API_BASE = os.environ.get("API_BASE", "http://localhost:80/api")

st.set_page_config(
    page_title="Minecraft 库存管家",
    page_icon="🧰",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ----------------- API helpers -----------------
def api_get(path: str, **kwargs) -> dict[str, Any]:
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=15, **kwargs)
        if r.status_code >= 400:
            return {"_error": r.json().get("error", r.text) if r.text else f"HTTP {r.status_code}"}
        return r.json()
    except Exception as e:
        return {"_error": str(e)}


def api_post(path: str, json: dict | None = None) -> dict[str, Any]:
    try:
        r = requests.post(f"{API_BASE}{path}", json=json or {}, timeout=60)
        if r.status_code >= 400:
            try:
                return {"_error": r.json().get("error", r.text)}
            except Exception:
                return {"_error": f"HTTP {r.status_code}: {r.text[:200]}"}
        return r.json()
    except Exception as e:
        return {"_error": str(e)}


def api_delete(path: str) -> dict[str, Any]:
    try:
        r = requests.delete(f"{API_BASE}{path}", timeout=15)
        if r.status_code >= 400:
            return {"_error": r.text}
        return r.json()
    except Exception as e:
        return {"_error": str(e)}


# ----------------- Sidebar: connection -----------------
def render_sidebar() -> dict[str, Any]:
    with st.sidebar:
        st.title("🤖 机器人控制台")
        status = api_get("/bot/status")

        s_label_map = {
            "disconnected": ("⚪", "未连线"),
            "connecting": ("🟡", "连线中"),
            "connected": ("🟢", "已登录"),
            "spawned": ("🟢", "已上线"),
            "error": ("🔴", "错误"),
        }
        emo, label = s_label_map.get(status.get("status", "disconnected"), ("⚪", "未知"))
        st.markdown(f"### 状态：{emo} **{label}**")
        st.caption(status.get("message", ""))

        if status.get("position"):
            p = status["position"]
            st.caption(
                f"位置：{p.get('dimension', '?')} ({p['x']}, {p['y']}, {p['z']})"
            )
        if status.get("health") is not None:
            st.caption(f"❤️ {status['health']:.0f}　🍗 {status.get('food', 0):.0f}")

        st.divider()
        st.subheader("连线设定")

        with st.form("connect_form", clear_on_submit=False):
            host = st.text_input("伺服器位址", value=st.session_state.get("host", "localhost"))
            port = st.number_input("连接埠", min_value=1, max_value=65535, value=int(st.session_state.get("port", 25565)))
            username = st.text_input("机器人名称", value=st.session_state.get("username", "InvBot"))
            version = st.text_input("游戏版本（留空自动侦测）", value=st.session_state.get("version", ""))
            auth = st.selectbox("登录方式", ["offline", "microsoft"], index=0)

            col1, col2 = st.columns(2)
            connect_clicked = col1.form_submit_button("🔌 连线", use_container_width=True, type="primary")
            disconnect_clicked = col2.form_submit_button("⏏️ 离线", use_container_width=True)

        if connect_clicked:
            st.session_state.update({"host": host, "port": port, "username": username, "version": version})
            with st.spinner("连线中…可能需要几秒"):
                payload = {
                    "host": host,
                    "port": int(port),
                    "username": username,
                    "auth": auth,
                }
                if version.strip():
                    payload["version"] = version.strip()
                res = api_post("/bot/connect", payload)
            if res.get("_error"):
                st.error(f"连线失败：{res['_error']}")
            else:
                st.success("连线成功！")
                st.rerun()

        if disconnect_clicked:
            api_post("/bot/disconnect")
            st.info("已要求离线")
            st.rerun()

        st.divider()
        st.subheader("快速指令")
        chat_msg = st.text_input("聊天 / 指令", placeholder="例如：/home", key="chat_input")
        if st.button("📨 送出", use_container_width=True):
            if chat_msg.strip():
                res = api_post("/bot/chat", {"message": chat_msg.strip()})
                if res.get("_error"):
                    st.error(res["_error"])
                else:
                    st.success("已送出")

        if st.button("🔄 重新整理状态", use_container_width=True):
            st.rerun()

        return status


# ----------------- Helpers -----------------
def fmt_box_stack_single(item: dict) -> str:
    boxes, stacks, singles = item["boxes"], item["stacks"], item["singles"]
    parts = []
    if boxes > 0:
        parts.append(f"{boxes} 箱")
    if stacks > 0:
        parts.append(f"{stacks} 组")
    if singles > 0 or not parts:
        parts.append(f"{singles} 个")
    return " - ".join(parts)


def fmt_box_stack_single_for(count: int, stack_size: int) -> str:
    per_box = stack_size * 27
    boxes = count // per_box
    rem = count - boxes * per_box
    stacks = rem // stack_size
    singles = rem - stacks * stack_size
    parts = []
    if boxes > 0:
        parts.append(f"{boxes} 箱")
    if stacks > 0:
        parts.append(f"{stacks} 组")
    if singles > 0 or not parts:
        parts.append(f"{singles} 个")
    return " - ".join(parts)


def require_online(status: dict) -> bool:
    if status.get("status") != "spawned":
        st.warning("机器人尚未上线，请先在左侧连线。")
        return False
    return True


# ----------------- Pages -----------------
def page_dashboard(status: dict):
    st.header("📊 总库存（箱 - 组 - 个）")
    st.caption("汇总每个容器位置的最新快照，潜影盒会自动展开为内含物品。")

    data = api_get("/inventory/aggregate")
    if data.get("_error"):
        st.error(data["_error"])
        return

    items = data.get("items", [])
    if not items:
        st.info("还没有任何快照。先在 [扫描] 页面捕捉机器人背包或附近箱子吧。")
        return

    total_items = sum(i["total"] for i in items)
    total_kinds = len(items)
    total_boxes = sum(i["boxes"] for i in items)

    c1, c2, c3 = st.columns(3)
    c1.metric("物品种类", f"{total_kinds}")
    c2.metric("物品总数", f"{total_items:,}")
    c3.metric("等效满箱数", f"{total_boxes}")

    search = st.text_input("🔎 搜寻物品（中英皆可）", "")
    rows = []
    for it in items:
        if search and search.lower() not in it["displayName"].lower() and search.lower() not in it["itemName"].lower():
            continue
        rows.append({
            "中文名": it["displayName"],
            "ID": it["itemName"],
            "数量": it["total"],
            "箱-组-个": fmt_box_stack_single(it),
            "每组": it["stackSize"],
        })

    if not rows:
        st.info("没有符合条件的物品。")
        return

    df = pd.DataFrame(rows)
    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True,
        height=600,
        column_config={
            "数量": st.column_config.NumberColumn(format="%d"),
        },
    )


def page_scan(status: dict):
    st.header("📷 扫描容器")
    st.write("机器人就位后，可一键将背包或附近的箱子内容存进资料库。")

    if not require_online(status):
        return

    tab1, tab2 = st.tabs(["背包扫描", "附近箱子扫描"])

    with tab1:
        st.subheader("机器人背包")
        label = st.text_input("快照标签", value="主背包", key="inv_label")
        if st.button("📦 立即扫描背包", type="primary"):
            with st.spinner("扫描中…"):
                res = api_post("/snapshots/inventory", {"label": label})
            if res.get("_error"):
                st.error(res["_error"])
            else:
                st.success(f"成功！记录 {res.get('itemCount', 0)} 件物品（含展开后的潜影盒内容）。")
                time.sleep(0.5)
                st.rerun()

    with tab2:
        st.subheader("附近箱子 / 木桶 / 末影箱")
        col1, col2 = st.columns(2)
        chest_label = col1.text_input("快照标签", value="主仓库箱子", key="chest_label")
        scan_range = col2.number_input("搜索半径（格）", min_value=1, max_value=32, value=6)

        c1, c2 = st.columns(2)
        if c1.button("🔍 侦测附近容器", use_container_width=True):
            with st.spinner("搜寻中…"):
                res = api_get(f"/bot/nearby-chest?range={scan_range}")
            if res.get("_error"):
                st.error(res["_error"])
            elif res.get("found"):
                t = res["target"]
                st.success(f"找到 {t['name']}：({t['x']}, {t['y']}, {t['z']})")
            else:
                st.warning(f"附近 {scan_range} 格内没有箱子。")

        if c2.button("📥 开启并扫描", use_container_width=True, type="primary"):
            with st.spinner("正在开启箱子并解析…"):
                res = api_post("/snapshots/chest", {"label": chest_label, "range": scan_range})
            if res.get("_error"):
                st.error(res["_error"])
            else:
                t = res.get("target", {})
                st.success(
                    f"扫描完成！容器：{t.get('name')} @ ({t.get('x')},{t.get('y')},{t.get('z')}) — 共 {res.get('itemCount', 0)} 笔记录"
                )
                time.sleep(0.5)
                st.rerun()

    st.divider()
    st.subheader("👀 即时背包预览（不存档）")
    if st.button("看一下机器人现在身上有什么"):
        res = api_get("/bot/inventory-preview")
        if res.get("_error"):
            st.error(res["_error"])
        else:
            items = res.get("items", [])
            if not items:
                st.info("背包是空的。")
            else:
                df = pd.DataFrame([
                    {"槽位": it["slot"], "物品": it["displayName"], "ID": it["name"], "数量": it["count"]}
                    for it in items
                ])
                st.dataframe(df, hide_index=True, use_container_width=True)


def page_history(status: dict):
    st.header("📚 历史快照")

    data = api_get("/snapshots")
    if data.get("_error"):
        st.error(data["_error"])
        return

    snaps = data.get("snapshots", [])
    if not snaps:
        st.info("还没有任何快照。")
        return

    type_zh = {"inventory": "背包", "chest": "容器"}
    rows = []
    for s in snaps:
        loc = ""
        if s.get("x") is not None:
            loc = f"({s['x']},{s['y']},{s['z']})"
        rows.append({
            "ID": s["id"],
            "时间": s["takenAt"][:19].replace("T", " "),
            "类型": type_zh.get(s["sourceType"], s["sourceType"]),
            "标签": s["label"],
            "维度": s.get("dimension") or "",
            "位置": loc,
            "备注": s.get("notes") or "",
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, hide_index=True, use_container_width=True, height=350)

    st.divider()
    st.subheader("🔍 检视单一快照")
    snap_id = st.selectbox(
        "选择快照",
        options=[s["id"] for s in snaps],
        format_func=lambda i: next(
            f"#{s['id']} | {s['label']} | {s['takenAt'][:19].replace('T', ' ')}"
            for s in snaps if s["id"] == i
        ),
    )

    col_a, col_b = st.columns([1, 4])
    if col_a.button("🗑️ 删除此快照", type="secondary"):
        res = api_delete(f"/snapshots/{snap_id}")
        if res.get("_error"):
            st.error(res["_error"])
        else:
            st.success("已删除")
            st.rerun()

    detail = api_get(f"/snapshots/{snap_id}")
    if detail.get("_error"):
        st.error(detail["_error"])
        return

    items = detail.get("items", [])
    if not items:
        st.info("这个快照里没有物品。")
        return

    # Group by container; show top-level + nested shulker contents separately
    by_container: dict[str, list] = {}
    for it in items:
        by_container.setdefault(it["container"], []).append(it)

    for container, lst in by_container.items():
        with st.expander(f"📦 {container}（{len(lst)} 笔）", expanded=True):
            rows = []
            for it in lst:
                rows.append({
                    "物品": it["displayName"],
                    "ID": it["itemName"],
                    "数量": it["count"],
                    "箱-组-个": fmt_box_stack_single_for(it["count"], it["stackSize"]),
                    "潜影盒": "✓" if it["isShulker"] else "",
                })
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


def page_help():
    st.header("📖 使用说明")
    st.markdown("""
### 这是什么？
一个透过 [mineflayer](https://github.com/PrismarineJS/mineflayer) 连入 Minecraft 伺服器的 AI 机器人 + 库存管理网页。
机器人会以**外挂方式**（client-side 模拟玩家）打开箱子，读出里面的物品，并把每个**潜影盒**视为「一箱」自动展开内容。

### 工作流程
1. **左侧栏** 输入伺服器位址、机器人名称等资讯，按【连线】。
2. 等机器人在游戏里出生（状态变成🟢「已上线」）。
3. 切到 **扫描容器** 页面：
   - **背包扫描**：把机器人当下背包内的物品（含潜影盒内容）存档。
   - **附近箱子扫描**：机器人会找半径内的箱子/木桶/末影箱，打开并记录全部内容。
4. **总库存** 页面会用「**X 箱 - Y 组 - Z 个**」汇总你所有容器的最新内容。

### 关于「箱 - 组 - 个」
- **1 组**：一个槽位的最大堆叠（如石头 64、末影珍珠 16、剑 1）。
- **1 箱**：一个潜影盒大小 = 27 组（即 27 × 该物品最大堆叠数）。
- 系统依物品类型自动取得堆叠上限，所以工具/盔甲也会正确换算。

### 注意事项
- 离线伺服器：登录方式选 **offline** 即可。
- 正版伺服器：选 **microsoft** 时机器人帐号需要已经过 Mojang 验证（机器人首次登录时会出现于终端机）。
- 若伺服器有反外挂（NoCheatPlus 等），开太多箱子可能被踢。
- 末影箱内容是玩家专属、必须由机器人自己开过才会存到资料库。

### 后续可加（API 已经预留）
- 多机器人同时管理（`bot.ts` 改为多实例）
- 自动巡逻所有箱子
- 物品搬运 / 整理 AI
- 与 Discord 整合的低库存通知
""")


# ----------------- Main -----------------
def main():
    status = render_sidebar()

    page = st.sidebar.radio(
        "导航",
        ["📊 总库存", "📷 扫描容器", "📚 历史快照", "📖 说明"],
        label_visibility="collapsed",
    )

    if page == "📊 总库存":
        page_dashboard(status)
    elif page == "📷 扫描容器":
        page_scan(status)
    elif page == "📚 历史快照":
        page_history(status)
    else:
        page_help()


if __name__ == "__main__":
    main()
