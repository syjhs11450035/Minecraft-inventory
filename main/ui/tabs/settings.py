"""设定分页：伺服器连线设定 + 自动刷新 + 数量规则说明。"""

from __future__ import annotations

import streamlit as st

from main.ui.api import API_BASE


def tab_settings() -> None:
    with st.container(border=True):
        st.markdown("#### 🌐 伺服器连线设定")
        st.caption("以下设定会被左侧栏的【🚀 连线】按钮使用。")

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
                "游戏版本",
                value=st.session_state.get("version", ""),
                placeholder="留空自动侦测",
            )
            auth = st.selectbox(
                "登录方式",
                ["offline", "microsoft"],
                index=0 if st.session_state.get("auth", "offline") == "offline" else 1,
            )

            saved = st.form_submit_button(
                "💾 储存设定", type="primary", use_container_width=True
            )
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

    with st.container(border=True):
        st.markdown("#### ⏱️ 自动刷新")
        auto_refresh = st.toggle(
            "启用自动刷新（每 3 秒）",
            value=st.session_state.get("auto_refresh", False),
            help="机器人在线时持续刷新画面以同步最新状态。",
        )
        st.session_state.auto_refresh = auto_refresh

    with st.container(border=True):
        st.markdown("#### 📐 数量换算规则")
        st.markdown(
            """
            - **1 组 (stack)**：物品的最大堆叠（石头 64、末影珍珠 16、剑 1…，由游戏数据自动取值）  
            - **1 箱 (box)**：相当于一个潜影盒大小，固定 **27 组**  
            """
        )

    with st.container(border=True):
        st.markdown("#### 📦 潜影盒处理")
        st.markdown(
            """
            - 扫描时若侦测到潜影盒，会**自动展开**读取其内容并存入数据库  
            - 在「仓库总览」聚合时**只算内容物**，避免重复计算潜影盒本身  
            """
        )

    with st.container(border=True):
        st.markdown("#### 🔌 API")
        st.code(f"API_BASE = {API_BASE}", language="bash")
