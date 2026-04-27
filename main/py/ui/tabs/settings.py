"""设定分页：伺服器连线设定 + 自动刷新 + AI 设定 + HTTP 静态伺服器开关。"""

from __future__ import annotations

import streamlit as st

from main.py.ui.api import API_BASE, api_get, api_patch
from main.server import is_running as html_is_running, server_url, start_default, stop_default


def _server_settings_card() -> None:
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


def _auto_refresh_card() -> None:
    with st.container(border=True):
        st.markdown("#### ⏱️ 自动刷新")
        auto_refresh = st.toggle(
            "启用自动刷新（每 3 秒）",
            value=st.session_state.get("auto_refresh", False),
            help="机器人在线时持续刷新画面以同步最新状态。",
        )
        st.session_state.auto_refresh = auto_refresh


def _ai_settings_card() -> None:
    with st.container(border=True):
        st.markdown("#### 🤖 AI 助手（`ai!` 触发）")
        st.caption(
            "启用后，游戏内任何玩家在聊天用 `ai!你好` 起头的讯息会被送给 AI，"
            "回应（含关键字动作如『跟我來』『跳』『停下』）会自动回到聊天频道。"
        )
        cur = api_get("/settings")
        if cur.get("_error"):
            st.error(cur["_error"])
            return
        ai = cur.get("ai", {})

        enabled = st.toggle(
            "启用 AI",
            value=bool(ai.get("enabled", False)),
            key="ai_enabled_toggle",
        )
        reply_in_chat = st.toggle(
            "AI 回应自动回到游戏聊天",
            value=bool(ai.get("replyInChat", True)),
            key="ai_reply_toggle",
        )
        model = st.selectbox(
            "AI 模型",
            options=[
                "claude-haiku-4-5",
                "claude-sonnet-4-6",
                "claude-opus-4-7",
            ],
            index=["claude-haiku-4-5", "claude-sonnet-4-6", "claude-opus-4-7"].index(
                ai.get("model", "claude-sonnet-4-6")
            )
            if ai.get("model") in ("claude-haiku-4-5", "claude-sonnet-4-6", "claude-opus-4-7")
            else 1,
        )
        system_prompt = st.text_area(
            "系统提示词",
            value=ai.get("systemPrompt", ""),
            height=120,
        )
        if st.button("💾 储存 AI 设定", type="primary"):
            res = api_patch(
                "/settings",
                {
                    "ai": {
                        "enabled": enabled,
                        "model": model,
                        "systemPrompt": system_prompt,
                        "replyInChat": reply_in_chat,
                    }
                },
            )
            if res.get("_error"):
                st.error(res["_error"])
            else:
                st.toast("AI 设定已更新", icon="🤖")


def _http_server_card() -> None:
    with st.container(border=True):
        st.markdown("#### 🌍 内建 HTTP 静态伺服器（`/html`）")
        st.caption(
            "提供专案根目录下 `/html/` 资料夹做为静态网站。"
            "可作为外部仪表板或文件存取入口。"
        )
        running = html_is_running()
        c1, c2 = st.columns([2, 1])
        port = c1.number_input(
            "Port",
            min_value=1024,
            max_value=65535,
            value=int(st.session_state.get("html_port", 8000)),
            key="html_port_input",
        )
        st.session_state.html_port = int(port)

        if running:
            url = server_url()
            st.success(f"✅ 已启动：{url or '本机'}")
            if c2.button("⏹️ 停止伺服器", use_container_width=True):
                stop_default()
                st.session_state.html_server_enabled = False
                st.toast("HTTP 伺服器已停止", icon="⏹️")
                st.rerun()
        else:
            st.info("目前未启动")
            if c2.button("▶️ 启动伺服器", type="primary", use_container_width=True):
                try:
                    start_default(port=int(port))
                    st.session_state.html_server_enabled = True
                    st.toast("HTTP 伺服器已启动", icon="🌍")
                    st.rerun()
                except OSError as e:
                    st.error(f"启动失败（port 可能已被占用）：{e}")


def _info_cards() -> None:
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


def tab_settings() -> None:
    _server_settings_card()
    _ai_settings_card()
    _http_server_card()
    _auto_refresh_card()
    _info_cards()
