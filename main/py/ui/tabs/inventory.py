"""仓库分页：左 = 物品总览表格，右 = 操作按钮 + 统计卡。"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from main.py.ui.api import api_get, fetch_areas
from main.py.ui.dialogs import dialog_scan_chest, dialog_scan_inventory
from main.py.ui.icons import icon_for


def tab_inventory(is_online: bool) -> None:
    left, right = st.columns([3, 1])

    # ---- 右侧：操作按钮 ----
    with right:
        with st.container(border=True):
            st.markdown("**🔧 操作**")
            if st.button(
                "📦 扫描背包",
                use_container_width=True,
                type="primary",
                disabled=not is_online,
            ):
                dialog_scan_inventory()
            if st.button(
                "📥 扫描附近箱子",
                use_container_width=True,
                disabled=not is_online,
            ):
                dialog_scan_chest()
            if st.button("🔄 重整资料", use_container_width=True):
                st.rerun()

        if not is_online:
            st.info("机器人未上线，先到「设定」填妥连线参数。")

    # ---- 左侧：表格 ----
    items: list[dict] = []
    with left:
        data = api_get("/inventory/aggregate")
        if data.get("_error"):
            st.error(data["_error"])
            return

        items = data.get("items", [])

        # 区域筛选
        areas = fetch_areas()
        f_opts: list[tuple[str, Any]] = [("🌐 全部区域", "__all__"), ("📁 其他（未分类）", None)]
        for a in areas:
            f_opts.append((f"📦 {a['name']}", a["id"]))
        f_labels = [o[0] for o in f_opts]
        sel = st.selectbox("筛选区域", range(len(f_labels)), format_func=lambda i: f_labels[i])
        filter_val = f_opts[sel][1]

        if filter_val != "__all__":
            sn_data = api_get("/snapshots")
            allowed_keys: set[str] = set()
            for s in sn_data.get("snapshots", []):
                if s.get("areaId") == filter_val:
                    allowed_keys.add(s["sourceKey"])
            items = [it for it in items if it.get("sourceKey") in allowed_keys]

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
                    "图片": icon_for(it["itemName"]),
                    "名称": it["displayName"],
                    "箱数": it["boxes"],
                    "组数": it["stacks"],
                    "个数": it["singles"],
                }
            )

        if not rows:
            st.info("没有符合条件的物品。")
        else:
            df = pd.DataFrame(rows)
            st.dataframe(
                df,
                hide_index=True,
                use_container_width=True,
                height=560,
                column_config={
                    "图片": st.column_config.TextColumn(width="small"),
                    "箱数": st.column_config.NumberColumn(width="small"),
                    "组数": st.column_config.NumberColumn(width="small"),
                    "个数": st.column_config.NumberColumn(width="small"),
                },
            )

    # ---- 右侧：统计卡（放按钮下方）----
    with right:
        total_items = sum(i["total"] for i in items)
        total_kinds = len(items)
        total_boxes = sum(i["boxes"] for i in items)

        st.markdown(
            f'<div class="stat-card"><div class="label">物品种类</div>'
            f'<div class="value">{total_kinds}</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="stat-card"><div class="label">物品总数</div>'
            f'<div class="value">{total_items:,}</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="stat-card"><div class="label">等效满箱</div>'
            f'<div class="value">{total_boxes}</div></div>',
            unsafe_allow_html=True,
        )
