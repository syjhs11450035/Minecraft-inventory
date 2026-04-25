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
    "chest": "📦", "trapped_chest": "📦", "barrel": "🛢️", "shulker_box": "📦",
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


def api_patch(path: str, json: dict | None = None) -> dict[str, Any]:
    try:
        r = requests.patch(f"{API_BASE}{path}", json=json or {}, timeout=15)
        if r.status_code >= 400:
            try:
                return {"_error": r.json().get("error", r.text)}
            except Exception:
                return {"_error": f"HTTP {r.status_code}"}
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


# ----------------- 状态 -----------------
def status_pill(status: dict) -> str:
    s = status.get("status", "disconnected")
    if s == "spawned":
        return '<span class="status-pill status-online">🟢 已上线</span>'
    if s in ("connecting", "connected"):
        return '<span class="status-pill status-busy">🟡 连线中</span>'
    if s == "error":
        return '<span class="status-pill status-error">🔴 错误</span>'
    return '<span class="status-pill status-offline">⚪ 已离线</span>'


# ----------------- 区域 helpers -----------------
def fetch_areas() -> list[dict]:
    data = api_get("/areas")
    if data.get("_error"):
        return []
    return data.get("areas", [])


def area_select_options(areas: list[dict]) -> list[tuple[str, int | None]]:
    """返回 [(显示名, area_id 或 None)]，含「其他 / 未分类」选项。"""
    opts: list[tuple[str, int | None]] = [("📁 其他（未分类）", None)]
    for a in areas:
        opts.append((f"📦 {a['name']}", a["id"]))
    return opts


# ----------------- 扫描对话框 -----------------
@st.dialog("📦 扫描背包 — 选择存放区域")
def dialog_scan_inventory():
    areas = fetch_areas()
    opts = area_select_options(areas)
    labels = [o[0] for o in opts]

    with st.form("scan_inv_form"):
        st.caption("机器人当前背包内容会存为一笔快照，潜影盒会自动展开。")
        selected = st.selectbox("归类至区域", labels, index=0)
        label_in = st.text_input("快照标签", value="主背包")

        c1, c2 = st.columns(2)
        ok = c1.form_submit_button("✅ 确认扫描", use_container_width=True, type="primary")
        cancel = c2.form_submit_button("✖️ 取消", use_container_width=True)

        if cancel:
            st.rerun()
        if ok:
            area_id = next(o[1] for o in opts if o[0] == selected)
            with st.spinner("扫描背包中…"):
                res = api_post(
                    "/snapshots/inventory",
                    {"label": label_in.strip() or "主背包", "areaId": area_id},
                )
            if res.get("_error"):
                st.error(res["_error"])
            else:
                st.toast(f"已记录 {res.get('itemCount', 0)} 笔物品", icon="📦")
                time.sleep(0.4)
                st.rerun()


@st.dialog("📥 扫描附近箱子 — 选择存放区域")
def dialog_scan_chest():
    areas = fetch_areas()
    opts = area_select_options(areas)
    labels = [o[0] for o in opts]

    with st.form("scan_chest_form"):
        st.caption("机器人会在指定半径内寻找箱子/木桶/末影箱并外挂方式开启。")
        selected = st.selectbox("归类至区域", labels, index=0)
        label_in = st.text_input("快照标签", value="未命名容器")
        range_in = st.number_input("搜索半径（格）", min_value=1, max_value=32, value=6)

        c1, c2 = st.columns(2)
        ok = c1.form_submit_button("✅ 确认扫描", use_container_width=True, type="primary")
        cancel = c2.form_submit_button("✖️ 取消", use_container_width=True)

        if cancel:
            st.rerun()
        if ok:
            area_id = next(o[1] for o in opts if o[0] == selected)
            with st.spinner("外挂方式开启箱子中…"):
                res = api_post(
                    "/snapshots/chest",
                    {
                        "label": label_in.strip() or "未命名容器",
                        "range": int(range_in),
                        "areaId": area_id,
                    },
                )
            if res.get("_error"):
                st.error(res["_error"])
            else:
                t = res.get("target", {})
                st.toast(
                    f"已记录 {t.get('name', '?')}：{res.get('itemCount', 0)} 笔",
                    icon="📥",
                )
                time.sleep(0.4)
                st.rerun()


# ----------------- 侧边栏（精简版）-----------------
def render_sidebar(status: dict) -> bool:
    is_online = status.get("status") == "spawned"

    with st.sidebar:
        st.title("🎮 机器人控制中心")
        st.markdown(status_pill(status), unsafe_allow_html=True)
        msg = status.get("message") or ""
        if msg:
            st.caption(msg)

        # 显示当前生效的连线参数（只读，编辑请到「设定」分页）
        host = st.session_state.get("host", "localhost")
        port = st.session_state.get("port", 25565)
        username = st.session_state.get("username", "InvBot")
        st.caption(f"🌐 `{host}:{port}` 　🤖 `{username}`")

        st.divider()

        c1, c2 = st.columns(2)
        if c1.button("🚀 连线", use_container_width=True, disabled=is_online, type="primary"):
            payload = {
                "host": host,
                "port": int(port),
                "username": username,
                "auth": st.session_state.get("auth", "offline"),
            }
            v = (st.session_state.get("version") or "").strip()
            if v:
                payload["version"] = v
            with st.spinner("连线中…"):
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

        # 机器人即时状态
        if is_online:
            with st.container(border=True):
                p = status.get("position") or {}
                if p:
                    st.markdown(
                        f"**📍 维度** `{p.get('dimension', '—')}`\n\n"
                        f"**X** `{p.get('x', 0)}` 　**Y** `{p.get('y', 0)}` 　**Z** `{p.get('z', 0)}`"
                    )
                health = status.get("health")
                food = status.get("food")
                if health is not None:
                    st.progress(min(1.0, max(0.0, health / 20)), text=f"❤️ {health:.0f}/20")
                if food is not None:
                    st.progress(min(1.0, max(0.0, food / 20)), text=f"🍗 {food:.0f}/20")

        st.divider()

        st.subheader("⚙️ 运作模式")
        st.radio(
            "选择模式：",
            ["📦 库存管理", "🤖 自动整理（开发中）"],
            label_visibility="collapsed",
            help="目前仅启用「库存管理」；自动整理为后续扩充功能。",
        )

        st.divider()

        auto_refresh = st.toggle(
            "⏱️ 自动刷新（每 3 秒）",
            value=st.session_state.get("auto_refresh", False),
            help="机器人在线时持续刷新画面以同步最新状态。",
        )
        st.session_state.auto_refresh = auto_refresh

        st.divider()

        st.subheader("💬 快速指令")
        with st.form("chat_form", clear_on_submit=True):
            chat_msg = st.text_input(
                "讯息 / 指令", placeholder="例：/home", label_visibility="collapsed"
            )
            sent = st.form_submit_button(
                "📨 送出", use_container_width=True, disabled=not is_online
            )
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
def tab_inventory(status: dict, is_online: bool, areas: list[dict]):
    st.markdown("### 📦 仓库总览（箱 - 组 - 个）")
    st.caption("汇总每个容器位置的最新快照，潜影盒会自动展开为内含物品。")

    # 快速扫描按钮（开启对话框）
    cc1, cc2, cc3, _ = st.columns([1, 1, 1, 3])
    if cc1.button("📦 扫描背包", use_container_width=True, type="primary", disabled=not is_online):
        dialog_scan_inventory()
    if cc2.button("📥 扫描附近箱子", use_container_width=True, disabled=not is_online):
        dialog_scan_chest()
    if cc3.button("🔄 重整资料", use_container_width=True):
        st.rerun()

    if not is_online:
        st.info("机器人尚未上线。可以先到「设定」分页填妥连线资讯，再回侧栏按【🚀 连线】。")

    data = api_get("/inventory/aggregate")
    if data.get("_error"):
        st.error(data["_error"])
        return

    items = data.get("items", [])
    if not items:
        st.info("还没有任何快照。请按上方【扫描背包】或【扫描附近箱子】开始建立资料。")
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


# ----------------- Tab 2: 箱子管理（区域 + 快照）-----------------
def tab_chests(status: dict, is_online: bool, areas: list[dict]):
    st.markdown("### 🗺️ 箱子管理")
    st.caption("管理所有「区域」（如：主仓库、附魔台旁、末影箱区…），并查看每个区域的快照。")

    # ---- 区域 CRUD ----
    st.markdown("#### 🏷️ 区域管理")

    # 新增区域
    with st.expander("➕ 新增区域", expanded=False):
        with st.form("new_area_form", clear_on_submit=True):
            n1, n2 = st.columns([1, 2])
            new_name = n1.text_input("名称", value="")
            new_desc = n2.text_input("描述（选填）", value="")
            submit = st.form_submit_button("✅ 建立", type="primary")
            if submit:
                if not new_name.strip():
                    st.warning("请填入区域名称")
                else:
                    res = api_post(
                        "/areas", {"name": new_name.strip(), "description": new_desc.strip() or None}
                    )
                    if res.get("_error"):
                        st.error(res["_error"])
                    else:
                        st.toast(f"区域「{new_name}」已建立", icon="🏷️")
                        st.rerun()

    if not areas:
        st.info("尚未建立任何区域。展开上方面板新增第一个区域，或在扫描时选择「其他」。")
    else:
        rows = []
        for a in areas:
            rows.append(
                {
                    "ID": a["id"],
                    "名称": a["name"],
                    "描述": a.get("description") or "",
                    "快照数": a.get("snapshotCount", 0),
                    "建立时间": (a.get("createdAt") or "")[:19].replace("T", " "),
                }
            )
        df_areas = pd.DataFrame(rows).set_index("ID")
        edited = st.data_editor(
            df_areas,
            use_container_width=True,
            num_rows="fixed",
            column_config={
                "名称": st.column_config.TextColumn(required=True, max_chars=80),
                "描述": st.column_config.TextColumn(max_chars=300),
                "快照数": st.column_config.NumberColumn(disabled=True),
                "建立时间": st.column_config.TextColumn(disabled=True),
            },
            key="areas_editor",
        )

        col_a, col_b, _ = st.columns([1, 1, 3])
        if col_a.button("💾 储存编辑", use_container_width=True, type="primary"):
            updated = 0
            for area_id, row in edited.iterrows():
                orig = next((a for a in areas if a["id"] == area_id), None)
                if not orig:
                    continue
                if (row["名称"] != orig["name"]) or (
                    (row["描述"] or "") != (orig.get("description") or "")
                ):
                    res = api_patch(
                        f"/areas/{area_id}",
                        {
                            "name": str(row["名称"]).strip(),
                            "description": (str(row["描述"]) or "").strip() or None,
                        },
                    )
                    if not res.get("_error"):
                        updated += 1
            if updated:
                st.toast(f"已更新 {updated} 个区域", icon="💾")
                st.rerun()
            else:
                st.info("没有侦测到任何变更。")

        delete_id = col_b.selectbox(
            "🗑️ 删除区域",
            options=[None] + [a["id"] for a in areas],
            format_func=lambda i: "—" if i is None else f"#{i} {next(a['name'] for a in areas if a['id']==i)}",
            key="del_area_select",
        )
        if delete_id is not None:
            if col_b.button("⚠️ 确认删除", use_container_width=True):
                res = api_delete(f"/areas/{delete_id}")
                if res.get("_error"):
                    st.error(res["_error"])
                else:
                    st.toast("已删除（该区域内的快照会变为「其他」）", icon="🗑️")
                    st.rerun()

    st.divider()

    # ---- 区域筛选 + 快照列表 ----
    st.markdown("#### 📜 快照清单（依区域筛选）")

    filter_opts: list[tuple[str, Any]] = [("🌐 全部", "__all__"), ("📁 其他（未分类）", None)]
    for a in areas:
        filter_opts.append((f"📦 {a['name']}", a["id"]))
    filter_labels = [o[0] for o in filter_opts]
    sel_idx = st.selectbox("筛选区域：", range(len(filter_labels)), format_func=lambda i: filter_labels[i])
    filter_val = filter_opts[sel_idx][1]

    sn_data = api_get("/snapshots")
    if sn_data.get("_error"):
        st.error(sn_data["_error"])
        return

    snaps = sn_data.get("snapshots", [])
    if filter_val != "__all__":
        snaps = [s for s in snaps if s.get("areaId") == filter_val]

    if not snaps:
        st.info("此条件下尚无快照。")
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
                "区域": s.get("areaName") or "（其他）",
                "标签": s["label"],
                "维度": s.get("dimension") or "",
                "位置": loc,
                "备注": s.get("notes") or "",
            }
        )
    df = pd.DataFrame(rows)
    st.dataframe(df, hide_index=True, use_container_width=True, height=300)

    st.divider()
    st.markdown("#### 🔍 检视单一快照")

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


# ----------------- Tab 3: 设定（连线设定搬到这里）-----------------
def tab_settings():
    st.markdown("### ⚙️ 系统设定")

    with st.container(border=True):
        st.markdown("#### 🌐 伺服器连线设定")
        st.caption("以下设定会被左侧栏的【🚀 连线】按钮使用。修改后无需储存，直接按连线即可。")

        with st.form("server_settings_form"):
            host = st.text_input(
                "伺服器位址", value=st.session_state.get("host", "localhost")
            )
            port = st.number_input(
                "连接埠",
                min_value=1,
                max_value=65535,
                value=int(st.session_state.get("port", 25565)),
            )
            username = st.text_input(
                "机器人名称", value=st.session_state.get("username", "InvBot")
            )
            version = st.text_input(
                "游戏版本", value=st.session_state.get("version", ""), placeholder="留空自动侦测"
            )
            auth = st.selectbox(
                "登录方式",
                ["offline", "microsoft"],
                index=0 if st.session_state.get("auth", "offline") == "offline" else 1,
                help="离线服选 offline；正版服选 microsoft（首次登入需在 API 终端机完成验证）",
            )

            saved = st.form_submit_button("💾 储存设定", type="primary", use_container_width=True)
            if saved:
                st.session_state.update(
                    {
                        "host": host,
                        "port": int(port),
                        "username": username,
                        "version": version,
                        "auth": auth,
                    }
                )
                st.toast("设定已储存", icon="💾")

    col_left, col_right = st.columns(2)
    with col_left:
        with st.container(border=True):
            st.markdown("#### 🤖 AI 决策（开发中）")
            st.toggle("启用 AI 自动判断（预留）", value=False, disabled=True)
            st.text_input("AI API 金钥", value="", type="password", disabled=True)
            st.caption("将用于整合 LLM 自动判断座标与整理逻辑，目前为预留接口。")

    with col_right:
        with st.container(border=True):
            st.markdown("#### 🔌 API 连线资讯")
            st.code(f"API_BASE = {API_BASE}", language="bash")

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
    for e in reversed(entries):
        ts = datetime.fromtimestamp(e["ts"] / 1000).strftime("%H:%M:%S")
        emo = level_emoji.get(e["level"], "•")
        lines.append(f"[{ts}] {emo} {e['message']}")

    log_text = "\n".join(lines)
    with st.container(border=True, height=480):
        st.code(log_text, language="bash")


# ----------------- Main -----------------
def main():
    # session_state 默认值
    st.session_state.setdefault("host", "localhost")
    st.session_state.setdefault("port", 25565)
    st.session_state.setdefault("username", "InvBot")
    st.session_state.setdefault("version", "")
    st.session_state.setdefault("auth", "offline")

    status = api_get("/bot/status")
    if status.get("_error"):
        st.error(f"无法连线 API：{status['_error']}")
        st.stop()

    is_online = render_sidebar(status)
    areas = fetch_areas()

    st.title("🤖 AI-Bot Minecraft 库存控制台")

    tabs = st.tabs(["📦 仓库", "🗺️ 箱子管理", "⚙️ 设定", "📊 日志"])
    with tabs[0]:
        tab_inventory(status, is_online, areas)
    with tabs[1]:
        tab_chests(status, is_online, areas)
    with tabs[2]:
        tab_settings()
    with tabs[3]:
        tab_logs()

    if st.session_state.get("auto_refresh") and is_online:
        time.sleep(3)
        st.rerun()


if __name__ == "__main__":
    main()
