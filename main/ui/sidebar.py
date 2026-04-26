"""侧边栏：状态显示 + 连线/离线 + 模式 + 手动刷新。"""

from __future__ import annotations

import streamlit as st

from main.ui.api import api_post
from main.ui.format import status_pill


def render_sidebar(status: dict) -> bool:
    is_online = status.get("status") == "spawned"

    with st.sidebar:
        st.title("🎮 控制中心")

        # 状态徽章
        st.markdown(status_pill(status), unsafe_allow_html=True)

        # IP / 名称
        host = st.session_state.get("host", "localhost")
        port = st.session_state.get("port", 25565)
        username = st.session_state.get("username", "InvBot")
        st.caption(f"🌐 `{host}:{port}`")
        st.caption(f"🤖 `{username}`")

        msg = status.get("message") or ""
        if msg:
            st.caption(msg)

        st.divider()

        # 连线 / 离线
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

        # 在线状态摘要
        if is_online:
            with st.container(border=True):
                p = status.get("position") or {}
                if p:
                    st.markdown(
                        f"**📍** `{p.get('dimension', '—')}`  "
                        f"`{p.get('x', 0)},{p.get('y', 0)},{p.get('z', 0)}`"
                    )
                health = status.get("health")
                food = status.get("food")
                if health is not None:
                    st.progress(min(1.0, max(0.0, health / 20)), text=f"❤️ {health:.0f}/20")
                if food is not None:
                    st.progress(min(1.0, max(0.0, food / 20)), text=f"🍗 {food:.0f}/20")

        st.divider()

        # 模式（仅显示库存管理）
        st.subheader("⚙️ 模式")
        st.radio("模式：", ["📦 库存管理"], label_visibility="collapsed")

        st.divider()
        if st.button("🔄 手动刷新", use_container_width=True):
            st.rerun()

    return is_online
