"""箱子管理分页：区域 CRUD + 快照清单 + 单一快照检视。"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from main.ui.api import api_delete, api_get, api_patch, api_post, fetch_areas
from main.ui.format import fmt_box_stack_single, split_box_stack_single
from main.ui.icons import icon_for


def _area_form_new() -> None:
    with st.expander("➕ 新增区域", expanded=False):
        with st.form("new_area_form", clear_on_submit=True):
            n1, n2 = st.columns([1, 2])
            new_name = n1.text_input("名称", value="")
            new_desc = n2.text_input("描述", value="")

            v1, v2, ext = st.columns(3)
            new_v1 = v1.text_input("顶点 1（x,y,z）", value="", placeholder="100,64,200")
            new_v2 = v2.text_input("顶点 2（x,y,z）", value="", placeholder="120,68,220")
            new_ext = ext.text_input("延伸于", value="", placeholder="例：主仓库")

            submit = st.form_submit_button("✅ 建立", type="primary")
            if submit:
                if not new_name.strip():
                    st.warning("请填入区域名称")
                else:
                    res = api_post(
                        "/areas",
                        {
                            "name": new_name.strip(),
                            "description": new_desc.strip() or None,
                            "vertex1": new_v1.strip() or None,
                            "vertex2": new_v2.strip() or None,
                            "extendsFrom": new_ext.strip() or None,
                        },
                    )
                    if res.get("_error"):
                        st.error(res["_error"])
                    else:
                        st.toast(f"区域「{new_name}」已建立", icon="🏷️")
                        st.rerun()


def _area_table(areas: list[dict]) -> None:
    rows = [
        {
            "ID": a["id"],
            "名称": a["name"],
            "描述": a.get("description") or "",
            "顶点1": a.get("vertex1") or "",
            "顶点2": a.get("vertex2") or "",
            "延伸于": a.get("extendsFrom") or "",
            "快照数": a.get("snapshotCount", 0),
        }
        for a in areas
    ]
    df = pd.DataFrame(rows).set_index("ID")
    edited = st.data_editor(
        df,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "名称": st.column_config.TextColumn(required=True, max_chars=80),
            "描述": st.column_config.TextColumn(max_chars=300),
            "顶点1": st.column_config.TextColumn(max_chars=60, help="格式：x,y,z"),
            "顶点2": st.column_config.TextColumn(max_chars=60, help="格式：x,y,z"),
            "延伸于": st.column_config.TextColumn(max_chars=80, help="所属上层区域名称"),
            "快照数": st.column_config.NumberColumn(disabled=True),
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
            changed = (
                str(row["名称"]) != str(orig["name"] or "")
                or str(row["描述"] or "") != str(orig.get("description") or "")
                or str(row["顶点1"] or "") != str(orig.get("vertex1") or "")
                or str(row["顶点2"] or "") != str(orig.get("vertex2") or "")
                or str(row["延伸于"] or "") != str(orig.get("extendsFrom") or "")
            )
            if changed:
                res = api_patch(
                    f"/areas/{area_id}",
                    {
                        "name": str(row["名称"]).strip(),
                        "description": (str(row["描述"]) or "").strip() or None,
                        "vertex1": (str(row["顶点1"]) or "").strip() or None,
                        "vertex2": (str(row["顶点2"]) or "").strip() or None,
                        "extendsFrom": (str(row["延伸于"]) or "").strip() or None,
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
        format_func=lambda i: "—" if i is None
        else f"#{i} {next(a['name'] for a in areas if a['id']==i)}",
        key="del_area_select",
    )
    if delete_id is not None and col_b.button("⚠️ 确认删除", use_container_width=True):
        res = api_delete(f"/areas/{delete_id}")
        if res.get("_error"):
            st.error(res["_error"])
        else:
            st.toast("已删除（区域内的快照会变为「其他」）", icon="🗑️")
            st.rerun()


def _snapshot_list(areas: list[dict]) -> list[dict]:
    sn_data = api_get("/snapshots")
    if sn_data.get("_error"):
        st.error(sn_data["_error"])
        return []

    snaps = sn_data.get("snapshots", [])
    f_opts: list[tuple[str, Any]] = [("🌐 全部", "__all__"), ("📁 其他（未分类）", None)]
    for a in areas:
        f_opts.append((f"📦 {a['name']}", a["id"]))
    f_labels = [o[0] for o in f_opts]
    sel = st.selectbox(
        "📜 快照清单（依区域筛选）",
        range(len(f_labels)),
        format_func=lambda i: f_labels[i],
        key="snap_filter",
    )
    filter_val = f_opts[sel][1]
    if filter_val != "__all__":
        snaps = [s for s in snaps if s.get("areaId") == filter_val]

    if not snaps:
        st.info("此条件下尚无快照。")
        return []

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
            }
        )
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True, height=260)
    return snaps


def _snapshot_detail(snaps: list[dict]) -> None:
    snap_id = st.selectbox(
        "🔍 检视快照",
        options=[s["id"] for s in snaps],
        format_func=lambda i: next(
            f"#{s['id']} | {s['label']} | {s['takenAt'][:19].replace('T', ' ')}"
            for s in snaps
            if s["id"] == i
        ),
    )

    col_a, _ = st.columns([1, 5])
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
                        "图片": icon_for(it["itemName"]),
                        "名称": it["displayName"],
                        "箱数": b,
                        "组数": sk,
                        "个数": sg,
                    }
                )
            st.dataframe(
                pd.DataFrame(crows),
                hide_index=True,
                use_container_width=True,
                column_config={"图片": st.column_config.TextColumn(width="small")},
            )


def tab_chests(is_online: bool) -> None:
    areas = fetch_areas()

    _area_form_new()
    if not areas:
        st.info("尚未建立任何区域。展开上方面板新增第一个区域，或在扫描时选择「其他」。")
    else:
        _area_table(areas)

    st.divider()
    snaps = _snapshot_list(areas)
    if snaps:
        _snapshot_detail(snaps)
