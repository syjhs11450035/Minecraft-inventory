import os
import time
from datetime import datetime
from typing import Any

import pandas as pd
import requests
import streamlit as st

API_BASE = os.environ.get("API_BASE", "http://localhost:80/api")

# ----------------- 物品图标对照 -----------------
ITEM_ICONS = {
    "diamond": "💎", "diamond_block": "💎", "diamond_ore": "💎",
    "iron_ingot": "🥈", "iron_block": "🥈", "iron_ore": "🥈", "raw_iron": "🪨",
    "gold_ingot": "🥇", "gold_block": "🥇", "gold_ore": "🥇", "raw_gold": "🪨",
    "emerald": "💚", "emerald_block": "💚", "emerald_ore": "💚",
    "redstone": "🔴", "redstone_block": "🔴", "redstone_ore": "🔴",
    "coal": "⚫", "coal_block": "⚫", "coal_ore": "⚫", "charcoal": "⚫",
    "lapis_lazuli": "🔵", "lapis_block": "🔵", "lapis_ore": "🔵",
    "netherite_ingot": "🟪", "netherite_block": "🟪", "ancient_debris": "🟪",
    "stone": "🧱", "cobblestone": "🪨", "deepslate": "🪨", "cobbled_deepslate": "🪨",
    "dirt": "🟫", "grass_block": "🌱", "podzol": "🟫", "mycelium": "🟪",
    "sand": "⏳", "red_sand": "🟧", "gravel": "⚪",
    "oak_log": "🪵", "spruce_log": "🪵", "birch_log": "🪵",
    "jungle_log": "🪵", "acacia_log": "🪵", "dark_oak_log": "🪵",
    "mangrove_log": "🪵", "cherry_log": "🌸", "bamboo_block": "🎋",
    "oak_planks": "🟫", "spruce_planks": "🟫", "birch_planks": "🟫",
    "water_bucket": "💧", "lava_bucket": "🔥", "milk_bucket": "🥛", "bucket": "🪣",
    "bread": "🍞", "cooked_beef": "🥩", "cooked_porkchop": "🥓",
    "cooked_chicken": "🍗", "cooked_mutton": "🍖", "cooked_salmon": "🐟",
    "apple": "🍎", "golden_apple": "🍏", "enchanted_golden_apple": "🍏",
    "carrot": "🥕", "potato": "🥔", "baked_potato": "🥔",
    "wheat": "🌾", "wheat_seeds": "🌱", "sugar_cane": "🎋", "melon_slice": "🍉",
    "pumpkin": "🎃", "cake": "🍰", "cookie": "🍪",
    "diamond_sword": "⚔️", "iron_sword": "⚔️", "stone_sword": "⚔️",
    "wooden_sword": "⚔️", "golden_sword": "⚔️", "netherite_sword": "⚔️",
    "diamond_pickaxe": "⛏️", "iron_pickaxe": "⛏️", "stone_pickaxe": "⛏️",
    "wooden_pickaxe": "⛏️", "golden_pickaxe": "⛏️", "netherite_pickaxe": "⛏️",
    "diamond_axe": "🪓", "iron_axe": "🪓", "stone_axe": "🪓",
    "wooden_axe": "🪓", "golden_axe": "🪓", "netherite_axe": "🪓",
    "diamond_shovel": "🥄", "iron_shovel": "🥄",
    "diamond_hoe": "🔨", "iron_hoe": "🔨",
    "bow": "🏹", "crossbow": "🏹", "arrow": "➡️", "spectral_arrow": "✨",
    "shield": "🛡️", "totem_of_undying": "🌟",
    "ender_pearl": "🟣", "ender_eye": "👁️", "ender_chest": "📦",
    "experience_bottle": "🧪", "potion": "🧪", "splash_potion": "🧪",
    "tnt": "💣", "fire_charge": "🔥", "flint_and_steel": "🔥",
    "torch": "🔦", "lantern": "🏮", "soul_torch": "🔵",
    "chest": "📦", "trapped_chest": "📦", "barrel": "🛢️",
    "shulker_box": "📦",
    "white_shulker_box": "⬜", "orange_shulker_box": "🟧", "magenta_shulker_box": "🟪",
    "light_blue_shulker_box": "🟦", "yellow_shulker_box": "🟨", "lime_shulker_box": "🟩",
    "pink_shulker_box": "🩷", "gray_shulker_box": "⬛", "light_gray_shulker_box": "⬜",
    "cyan_shulker_box": "🟦", "purple_shulker_box": "🟣", "blue_shulker_box": "🟦",
    "brown_shulker_box": "🟫", "green_shulker_box": "🟩", "red_shulker_box": "🟥",
    "black_shulker_box": "⬛",
    "elytra": "🪽", "trident": "🔱", "nautilus_shell": "🐚",
    "name_tag": "🏷️", "lead": "🪢", "compass": "🧭", "clock": "🕐",
    "map": "🗺️", "filled_map": "🗺️",
    "book": "📕", "written_book": "📖", "writable_book": "📓",
    "enchanted_book": "✨", "bookshelf": "📚",
    "music_disc_13": "💿", "jukebox": "🎵",
    "spawner": "🥚", "beacon": "💡", "conduit": "💡",
    "blaze_rod": "🔥", "blaze_powder": "🟡", "ghast_tear": "💧",
    "nether_star": "⭐", "dragon_egg": "🥚", "dragon_breath": "🌬️",
    "wither_skeleton_skull": "💀", "skeleton_skull": "💀",
    "egg": "🥚", "snowball": "❄️", "ice": "🧊", "packed_ice": "🧊",
    "obsidian": "🟪", "crying_obsidian": "🟪", "bedrock": "⬛",
    "string": "🧵", "feather": "🪶", "leather": "🟫", "rabbit_hide": "🟫",
    "iron_nugget": "🔘", "gold_nugget": "🔘",
    "saddle": "🐎", "carrot_on_a_stick": "🥕",
    "fishing_rod": "🎣", "cod": "🐟", "salmon": "🐟", "tropical_fish": "🐠",
    "pufferfish": "🐡",
}

DEFAULT_ICON = "🔹"


def icon_for(item_name: str) -> str:
    if item_name in ITEM_ICONS:
        return ITEM_ICONS[item_name]
    # 通用前缀匹配
    for key, ic in ITEM_ICONS.items():
        if item_name.endswith(key):
            return ic
    if "shulker_box" in item_name:
        return "📦"
    if "_log" in item_name or "_planks" in item_name:
        return "🪵"
    if "_ore" in item_name:
        return "🪨"
    if "_sword" in item_name:
        return "⚔️"
    if "_pickaxe" in item_name:
        return "⛏️"
    if "_axe" in item_name:
        return "🪓"
    if "_helmet" in item_name or "_chestplate" in item_name or "_leggings" in item_name or "_boots" in item_name:
        return "🛡️"
    return DEFAULT_ICON


# ----------------- 页面设定 -----------------
st.set_page_config(
    page_title="AI-Bot Minecraft 库存控制台",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] { background: #0f1419; }
        section[data-testid="stSidebar"] * { color: #e6edf3; }
        h1, h2, h3 { color: #1f2937; }
        .status-pill {
            display: inline-block; padding: 4px 12px; border-radius: 999px;
            font-weight: 600; font-size: 0.95rem;
        }
        .status-online  { background: #16a34a; color: white; }
        .status-busy    { background: #d97706; color: white; }
        .status-offline { background: #4b5563; color: white; }
        .status-error   { background: #dc2626; color: white; }
        .stat-card {
            background: linear-gradient(135deg, #1e3a8a, #3b82f6);
            color: white; padding: 16px; border-radius: 12px; text-align:center;
        }
        .stat-card .label { font-size: 0.8rem; opacity: 0.8; }
        .stat-card .value { font-size: 1.6rem; font-weight: 700; margin-top: 4px;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------- API helpers -----------------
def api_get(path: str, **kwargs) -> dict[str, Any]:
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=15, **kwargs)
        if r.status_code >= 400:
            try:
                return {"_error": r.json().get("error", r.text)}
            except Exception:
                return {"_error": f"HTTP {r.status_code}"}
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


# ----------------- 数学：箱-组-个 -----------------
def fmt_box_stack_single(boxes: int, stacks: int, singles: int) -> str:
    parts = []
    if boxes > 0:
        parts.append(f"{boxes} 箱")
    if stacks > 0:
        parts.append(f"{stacks} 组")
    if singles > 0 or not parts:
        parts.append(f"{singles} 个")
    return " - ".join(parts)


def split_box_stack_single(count: int, stack_size: int) -> tuple[int, int, int]:
    per_box = stack_size * 27
    boxes = count // per_box
    rem = count - boxes * per_box
    stacks = rem // stack_size
    singles = rem - stacks * stack_size
    return boxes, stacks, singles


# ----------------- 状态颜色 -----------------
def status_pill(status: dict) -> str:
    s = status.get("status", "disconnected")
    if s == "spawned":
        return '<span class="status-pill status-online">🟢 已上线</span>'
    if s in ("connecting", "connected"):
        return '<span class="status-pill status-busy">🟡 连线中</span>'
    if s == "error":
        return '<span class="status-pill status-error">🔴 错误</span>'
    return '<span class="status-pill status-offline">⚪ 已离线</span>'


# ----------------- 侧边栏 -----------------
def render_sidebar(status: dict) -> bool:
    is_online = status.get("status") == "spawned"

    with st.sidebar:
        st.title("🎮 机器人控制中心")
        st.markdown(status_pill(status), unsafe_allow_html=True)
        msg = status.get("message") or ""
        if msg:
            st.caption(msg)

        st.divider()
        st.subheader("🔌 连线设定")

        host = st.text_input("伺服器位址", value=st.session_state.get("host", "localhost"))
        port = st.number_input(
            "连接埠",
            min_value=1,
            max_value=65535,
            value=int(st.session_state.get("port", 25565)),
        )
        username = st.text_input("机器人名称", value=st.session_state.get("username", "InvBot"))
        version = st.text_input(
            "游戏版本", value=st.session_state.get("version", ""), placeholder="留空自动侦测"
        )
        auth = st.selectbox(
            "登录方式", ["offline", "microsoft"], index=0, help="离线服选 offline；正版服选 microsoft"
        )

        c1, c2 = st.columns(2)
        if c1.button("🚀 连线", use_container_width=True, disabled=is_online, type="primary"):
            st.session_state.update(
                {"host": host, "port": port, "username": username, "version": version}
            )
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
                st.toast("机器人已连线！", icon="🟢")
                st.rerun()

        if c2.button("🛑 离线", use_container_width=True, disabled=not is_online):
            api_post("/bot/disconnect")
            st.toast("已离线", icon="⚪")
            st.rerun()

        st.divider()

        # 模式选择（自动整理为预留功能）
        st.subheader("⚙️ 运作模式")
        st.radio(
            "选择模式：",
            ["📦 库存管理", "🤖 自动整理（开发中）"],
            label_visibility="collapsed",
            help="目前仅启用「库存管理」；自动整理为后续扩充功能。",
        )

        st.divider()

        # 自动刷新
        auto_refresh = st.toggle(
            "⏱️ 自动刷新（每 3 秒）",
            value=st.session_state.get("auto_refresh", False),
            help="机器人在线时持续刷新画面以同步最新状态。",
        )
        st.session_state.auto_refresh = auto_refresh

        st.divider()

        # 快速聊天
        st.subheader("💬 快速指令")
        with st.form("chat_form", clear_on_submit=True):
            chat_msg = st.text_input(
                "讯息 / 指令", placeholder="例：/home", label_visibility="collapsed"
            )
            sent = st.form_submit_button("📨 送出", use_container_width=True, disabled=not is_online)
            if sent and chat_msg.strip():
                res = api_post("/bot/chat", {"message": chat_msg.strip()})
                if res.get("_error"):
                    st.error(res["_error"])
                else:
                    st.toast("讯息已送出", icon="📨")

        if st.button("🔄 手动刷新", use_container_width=True):
            st.rerun()

    return is_online


# ----------------- Tab 1: 仓库 -----------------
def tab_inventory(status: dict, is_online: bool):
    col_main, col_side = st.columns([3, 1])

    with col_side:
        st.markdown("### 🤖 机器人资讯")
        cfg = status.get("config") or {}
        with st.container(border=True):
            st.markdown(f"**名称**　{cfg.get('username', '—')}")
            p = status.get("position") or {}
            if p:
                st.markdown(
                    f"**维度**　{p.get('dimension', '—')}\n\n"
                    f"**座标**　X `{p.get('x', 0)}`　Y `{p.get('y', 0)}`　Z `{p.get('z', 0)}`"
                )
            else:
                st.markdown("**位置**　—")
            health = status.get("health")
            food = status.get("food")
            if health is not None:
                st.progress(min(1.0, max(0.0, health / 20)), text=f"❤️ 血量　{health:.0f} / 20")
            if food is not None:
                st.progress(min(1.0, max(0.0, food / 20)), text=f"🍗 饱食度　{food:.0f} / 20")
            if not is_online:
                st.caption("（机器人未上线）")

        st.markdown("### 🛠️ 快速操作")
        if st.button(
            "📦 扫描背包",
            use_container_width=True,
            disabled=not is_online,
            type="primary",
        ):
            with st.spinner("扫描背包中…"):
                res = api_post("/snapshots/inventory", {"label": "主背包"})
            if res.get("_error"):
                st.error(res["_error"])
            else:
                st.toast(f"已记录 {res.get('itemCount', 0)} 笔物品", icon="📦")
                st.rerun()

        if st.button(
            "📥 扫描附近箱子",
            use_container_width=True,
            disabled=not is_online,
        ):
            with st.spinner("正在外挂方式开启箱子…"):
                res = api_post("/snapshots/chest", {"label": "附近容器", "range": 6})
            if res.get("_error"):
                st.error(res["_error"])
            else:
                t = res.get("target", {})
                st.toast(
                    f"已扫描 {t.get('name')} ({res.get('itemCount', 0)} 笔)", icon="📥"
                )
                st.rerun()

    with col_main:
        st.markdown("### 📦 仓库总览（箱 - 组 - 个）")
        st.caption("汇总每个容器位置的最新快照，潜影盒会自动展开为内含物品。")

        data = api_get("/inventory/aggregate")
        if data.get("_error"):
            st.error(data["_error"])
            return

        items = data.get("items", [])
        if not items:
            st.info("还没有任何快照。请按右侧【扫描背包】或【扫描附近箱子】开始建立资料。")
            return

        total_items = sum(i["total"] for i in items)
        total_kinds = len(items)
        total_boxes = sum(i["boxes"] for i in items)

        c1, c2, c3 = st.columns(3)
        c1.markdown(
            f'<div class="stat-card"><div class="label">物品种类</div><div class="value">{total_kinds}</div></div>',
            unsafe_allow_html=True,
        )
        c2.markdown(
            f'<div class="stat-card"><div class="label">物品总数</div><div class="value">{total_items:,}</div></div>',
            unsafe_allow_html=True,
        )
        c3.markdown(
            f'<div class="stat-card"><div class="label">等效满箱数</div><div class="value">{total_boxes}</div></div>',
            unsafe_allow_html=True,
        )

        st.markdown("&nbsp;")
        search = st.text_input("🔎 搜寻物品（中文 / 英文 ID）", "")

        rows = []
        for it in items:
            if (
                search
                and search.lower() not in it["displayName"].lower()
                and search.lower() not in it["itemName"].lower()
            ):
                continue
            rows.append(
                {
                    "图标": icon_for(it["itemName"]),
                    "中文名": it["displayName"],
                    "ID": it["itemName"],
                    "数量": it["total"],
                    "箱-组-个": fmt_box_stack_single(it["boxes"], it["stacks"], it["singles"]),
                    "每组": it["stackSize"],
                }
            )

        if not rows:
            st.info("没有符合条件的物品。")
            return

        df = pd.DataFrame(rows)
        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
            height=520,
            column_config={
                "图标": st.column_config.TextColumn(width="small"),
                "数量": st.column_config.NumberColumn(format="%d"),
                "每组": st.column_config.NumberColumn(width="small"),
            },
        )


# ----------------- Tab 2: 箱子管理 -----------------
def tab_chests(status: dict, is_online: bool):
    st.markdown("### 🗺️ 箱子管理")
    st.caption("查看所有曾扫描过的容器位置；可重新扫描或删除快照。")

    # 侦测附近箱子 + 自订标签扫描
    with st.expander("🔍 侦测附近容器（指定半径与标签）", expanded=False):
        with st.form("scan_with_label"):
            cc1, cc2, cc3 = st.columns([2, 1, 1])
            label_in = cc1.text_input("快照标签", value="主仓库箱子")
            range_in = cc2.number_input("搜索半径", min_value=1, max_value=32, value=6)
            cc3.markdown("&nbsp;")
            scan_btn = cc3.form_submit_button(
                "📥 开启并扫描", use_container_width=True, disabled=not is_online, type="primary"
            )
            if scan_btn:
                with st.spinner("外挂方式开箱中…"):
                    res = api_post("/snapshots/chest", {"label": label_in, "range": int(range_in)})
                if res.get("_error"):
                    st.error(res["_error"])
                else:
                    t = res.get("target", {})
                    st.success(
                        f"已记录 {t.get('name')} @ ({t.get('x')},{t.get('y')},{t.get('z')}) — {res.get('itemCount', 0)} 笔"
                    )
                    st.rerun()

    data = api_get("/snapshots")
    if data.get("_error"):
        st.error(data["_error"])
        return

    snaps = data.get("snapshots", [])
    if not snaps:
        st.info("尚无任何箱子快照。")
        return

    type_zh = {"inventory": "📦 背包", "chest": "🗄️ 容器"}
    rows = []
    for s in snaps:
        loc = ""
        if s.get("x") is not None:
            loc = f"({s['x']},{s['y']},{s['z']})"
        rows.append(
            {
                "ID": s["id"],
                "时间": s["takenAt"][:19].replace("T", " "),
                "类型": type_zh.get(s["sourceType"], s["sourceType"]),
                "标签": s["label"],
                "维度": s.get("dimension") or "",
                "位置": loc,
                "备注": s.get("notes") or "",
            }
        )
    df = pd.DataFrame(rows)
    st.dataframe(df, hide_index=True, use_container_width=True, height=300)

    st.divider()
    st.markdown("### 🔍 检视单一快照")
    snap_id = st.selectbox(
        "选择快照",
        options=[s["id"] for s in snaps],
        format_func=lambda i: next(
            f"#{s['id']} | {s['label']} | {s['takenAt'][:19].replace('T', ' ')}"
            for s in snaps
            if s["id"] == i
        ),
    )

    col_a, col_b = st.columns([1, 4])
    if col_a.button("🗑️ 删除此快照", type="secondary"):
        res = api_delete(f"/snapshots/{snap_id}")
        if res.get("_error"):
            st.error(res["_error"])
        else:
            st.toast("快照已删除", icon="🗑️")
            st.rerun()

    detail = api_get(f"/snapshots/{snap_id}")
    if detail.get("_error"):
        st.error(detail["_error"])
        return

    items = detail.get("items", [])
    if not items:
        st.info("这个快照里没有物品。")
        return

    by_container: dict[str, list] = {}
    for it in items:
        by_container.setdefault(it["container"], []).append(it)

    for container, lst in by_container.items():
        with st.expander(f"📦 {container}（{len(lst)} 笔）", expanded=True):
            crows = []
            for it in lst:
                b, sk, sg = split_box_stack_single(it["count"], it["stackSize"])
                crows.append(
                    {
                        "图标": icon_for(it["itemName"]),
                        "物品": it["displayName"],
                        "ID": it["itemName"],
                        "数量": it["count"],
                        "箱-组-个": fmt_box_stack_single(b, sk, sg),
                        "潜影盒": "✓" if it["isShulker"] else "",
                    }
                )
            st.dataframe(
                pd.DataFrame(crows),
                hide_index=True,
                use_container_width=True,
                column_config={"图标": st.column_config.TextColumn(width="small")},
            )


# ----------------- Tab 3: 设定 -----------------
def tab_settings():
    st.markdown("### ⚙️ 系统设定")

    col_left, col_right = st.columns(2)
    with col_left:
        with st.container(border=True):
            st.markdown("#### 🌐 伺服器预设值")
            st.text_input(
                "预设位址",
                value=st.session_state.get("host", "localhost"),
                key="host_setting",
                disabled=True,
                help="实际连线请使用左侧栏的输入框。",
            )
            st.number_input(
                "预设连接埠",
                value=int(st.session_state.get("port", 25565)),
                disabled=True,
            )
            st.text_input(
                "预设机器人名称",
                value=st.session_state.get("username", "InvBot"),
                disabled=True,
            )
            st.caption("以上数值由「连线设定」页同步显示；修改请到左侧栏。")

    with col_right:
        with st.container(border=True):
            st.markdown("#### 🤖 AI 决策（开发中）")
            st.toggle("启用 AI 自动判断（预留）", value=False, disabled=True)
            st.text_input("AI API 金钥", value="", type="password", disabled=True)
            st.caption("将用于整合 LLM 自动判断座标与整理逻辑，目前为预留接口。")

    st.divider()

    with st.container(border=True):
        st.markdown("#### 📐 数量换算规则")
        st.markdown(
            """
            - **1 组 (stack)**：物品的最大堆叠（石头 64、末影珍珠 16、剑 1…，由游戏数据自动取值）  
            - **1 箱 (box)**：相当于一个潜影盒大小，固定 **27 组**  
            - 系统会以 `数量 = X 箱 + Y 组 + Z 个` 的形式自动换算  
            """
        )

    with st.container(border=True):
        st.markdown("#### 📦 潜影盒处理")
        st.markdown(
            """
            - 扫描时若侦测到潜影盒，会**自动展开**读取其内容并存入数据库  
            - 在「仓库总览」聚合时会**只算内容物**，避免重复计算潜影盒本身  
            - 容器路径会以 `主背包 → 紫色潜影盒#14` 之类的方式标示  
            """
        )

    with st.container(border=True):
        st.markdown("#### 🔌 API 连线资讯")
        st.code(f"API_BASE = {API_BASE}", language="bash")


# ----------------- Tab 4: 日志 -----------------
def tab_logs():
    st.markdown("### 📊 系统日志")
    st.caption("最近 200 条事件（机器人状态变化、聊天讯息、扫描结果、错误）")

    cc1, cc2 = st.columns([1, 5])
    if cc1.button("🗑️ 清空日志", use_container_width=True):
        api_delete("/bot/logs")
        st.rerun()

    data = api_get("/bot/logs", params={"limit": 200})
    if data.get("_error"):
        st.error(data["_error"])
        return

    entries = data.get("entries", [])
    if not entries:
        st.info("尚无日志资料。")
        return

    level_emoji = {"info": "ℹ️", "warn": "⚠️", "error": "❌", "chat": "💬", "system": "🛠️"}
    lines = []
    for e in reversed(entries):  # newest first
        ts = datetime.fromtimestamp(e["ts"] / 1000).strftime("%H:%M:%S")
        emo = level_emoji.get(e["level"], "•")
        lines.append(f"[{ts}] {emo} {e['message']}")

    log_text = "\n".join(lines)
    with st.container(border=True, height=480):
        st.code(log_text, language="bash")


# ----------------- Main -----------------
def main():
    status = api_get("/bot/status")
    if status.get("_error"):
        st.error(f"无法连线 API：{status['_error']}")
        st.stop()

    is_online = render_sidebar(status)

    st.title("🤖 AI-Bot Minecraft 库存控制台")

    tabs = st.tabs(["📦 仓库", "🗺️ 箱子管理", "⚙️ 设定", "📊 日志"])
    with tabs[0]:
        tab_inventory(status, is_online)
    with tabs[1]:
        tab_chests(status, is_online)
    with tabs[2]:
        tab_settings()
    with tabs[3]:
        tab_logs()

    if st.session_state.get("auto_refresh") and is_online:
        time.sleep(3)
        st.rerun()


if __name__ == "__main__":
    main()
