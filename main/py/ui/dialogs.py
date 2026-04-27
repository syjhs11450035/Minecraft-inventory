"""扫描背包 / 扫描箱子的弹出对话框。"""

from __future__ import annotations

import time

import streamlit as st

from main.py.ui.api import api_post, area_select_options, fetch_areas


@st.dialog("📦 扫描背包 — 选择存放区域")
def dialog_scan_inventory() -> None:
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
def dialog_scan_chest() -> None:
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
