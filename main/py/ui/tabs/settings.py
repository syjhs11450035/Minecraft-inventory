"""设定分页：所有设定都持久化在后台 JSON 档（/api/settings）。"""

from __future__ import annotations

import streamlit as st

from main.py.ui.api import API_BASE, fetch_settings, update_settings
from main.server import (
    is_running as html_is_running,
    server_url,
    start_default,
    stop_default,
)

MODELS = ["claude-haiku-4-5", "claude-sonnet-4-6", "claude-opus-4-7"]


def _connection_card(settings: dict) -> None:
    conn = settings.get("connection") or {}
    with st.container(border=True):
        st.markdown("#### 🌐 伺服器连线设定")
        st.caption("会自动存档到后台 JSON，下次重开也不用再设。")

        with st.form("server_settings_form"):
            host = st.text_input("伺服器位址", value=conn.get("host", "localhost"))
            port = st.number_input(
                "连接埠", min_value=1, max_value=65535,
                value=int(conn.get("port", 25565)),
            )
            username = st.text_input("机器人名称", value=conn.get("username", "InvBot"))
            version = st.text_input(
                "游戏版本",
                value=conn.get("version", ""),
                placeholder="留空自动侦测",
            )
            auth_idx = 0 if conn.get("auth", "offline") == "offline" else 1
            auth = st.selectbox("登录方式", ["offline", "microsoft"], index=auth_idx)

            saved = st.form_submit_button(
                "💾 储存设定", type="primary", use_container_width=True
            )
            if saved:
                res = update_settings({
                    "connection": {
                        "host": host,
                        "port": int(port),
                        "username": username,
                        "version": version,
                        "auth": auth,
                    }
                })
                if res.get("_error"):
                    st.error(res["_error"])
                else:
                    # 同步 session state，避免 sidebar 还看到旧值
                    st.session_state.update({
                        "host": host, "port": int(port),
                        "username": username, "version": version, "auth": auth,
                    })
                    st.toast("连线设定已存档", icon="💾")
                    st.rerun()


def _ui_card(settings: dict) -> None:
    ui = settings.get("ui") or {}
    with st.container(border=True):
        st.markdown("#### ⏱️ 自动刷新")
        cur = bool(ui.get("autoRefresh", False))
        new_val = st.toggle(
            "启用自动刷新（每 3 秒）",
            value=cur,
            help="机器人在线时持续刷新画面以同步最新状态。",
            key="ui_auto_refresh_toggle",
        )
        if new_val != cur:
            update_settings({"ui": {"autoRefresh": new_val}})
            st.session_state["auto_refresh"] = new_val
            st.toast("已存档", icon="💾")
            st.rerun()


def _ai_card(settings: dict) -> None:
    ai = settings.get("ai") or {}
    with st.container(border=True):
        st.markdown("#### 🤖 AI 助手（`ai!` 触发）")
        st.caption(
            "启用后，游戏内任何玩家在聊天用 `ai!你好` 起头的讯息会送给 AI；"
            "回应（含『跟我來』『跳』『停下』等关键字动作）会自动回到聊天频道。"
        )

        with st.form("ai_settings_form"):
            enabled = st.toggle("启用 AI", value=bool(ai.get("enabled", False)))
            reply_in_chat = st.toggle(
                "AI 回应自动回到游戏聊天",
                value=bool(ai.get("replyInChat", True)),
            )
            cur_model = ai.get("model", "claude-sonnet-4-6")
            model = st.selectbox(
                "AI 模型",
                options=MODELS,
                index=MODELS.index(cur_model) if cur_model in MODELS else 1,
            )
            system_prompt = st.text_area(
                "系统提示词", value=ai.get("systemPrompt", ""), height=120,
            )
            saved = st.form_submit_button(
                "💾 储存 AI 设定", type="primary", use_container_width=True
            )
            if saved:
                res = update_settings({
                    "ai": {
                        "enabled": enabled,
                        "model": model,
                        "systemPrompt": system_prompt,
                        "replyInChat": reply_in_chat,
                    }
                })
                if res.get("_error"):
                    st.error(res["_error"])
                else:
                    st.toast("AI 设定已存档", icon="🤖")
                    st.rerun()


def _http_server_card(settings: dict) -> None:
    html = settings.get("htmlServer") or {}
    with st.container(border=True):
        st.markdown("#### 🌍 内建 HTTP 静态伺服器（`/html`）")
        st.caption(
            "提供专案根目录下 `/html/` 资料夹做为静态网站。"
            "设定会存档，下次启动 Streamlit 时若 `enabled=True` 会自动开。"
        )

        running = html_is_running()
        c1, c2 = st.columns([2, 1])
        port = c1.number_input(
            "Port",
            min_value=1024,
            max_value=65535,
            value=int(html.get("port", 8000)),
            key="html_port_input",
        )

        if running:
            url = server_url()
            st.success(f"✅ 已启动：{url or '本机'}")
            if c2.button("⏹️ 停止伺服器", use_container_width=True):
                stop_default()
                update_settings({"htmlServer": {"enabled": False, "port": int(port)}})
                st.session_state["html_server_enabled"] = False
                st.toast("HTTP 伺服器已停止（设定也存档）", icon="⏹️")
                st.rerun()
        else:
            st.info("目前未启动")
            if c2.button("▶️ 启动伺服器", type="primary", use_container_width=True):
                try:
                    start_default(port=int(port))
                    update_settings({"htmlServer": {"enabled": True, "port": int(port)}})
                    st.session_state["html_server_enabled"] = True
                    st.toast("HTTP 伺服器已启动（设定也存档）", icon="🌍")
                    st.rerun()
                except OSError as e:
                    st.error(f"启动失败（port 可能已被占用）：{e}")

        # 若使用者只是想调 port 不启动，也提供单独存档
        if not running and int(port) != int(html.get("port", 8000)):
            if st.button("💾 仅存档 Port", use_container_width=True):
                update_settings({"htmlServer": {"port": int(port)}})
                st.toast("Port 已存档", icon="💾")
                st.rerun()


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
        st.caption("所有设定都会存到后台的 `data/settings.json`。")


def tab_settings() -> None:
    settings = fetch_settings()
    if not settings:
        st.error("无法读取后台设定，请确认 API 服务有跑起来。")
        return
    _connection_card(settings)
    _ai_card(settings)
    _http_server_card(settings)
    _ui_card(settings)
    _info_cards()
