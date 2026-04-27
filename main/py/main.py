"""核心进入点：组合所有模块、设定页面、画 sidebar 与 tabs。"""

from __future__ import annotations

import time

import streamlit as st

from main.py.ui.api import api_get, fetch_settings
from main.py.ui.sidebar import render_sidebar
from main.py.ui.styles import apply_styles
from main.py.ui.tabs.chests import tab_chests
from main.py.ui.tabs.inventory import tab_inventory
from main.py.ui.tabs.logs import tab_logs
from main.py.ui.tabs.misc import tab_misc
from main.py.ui.tabs.settings import tab_settings
from main.server import is_running as html_is_running, start_default


def _set_page_config_once() -> None:
    """st.set_page_config 一个 session 只能呼叫一次。"""
    if st.session_state.get("_page_config_set"):
        return
    st.set_page_config(
        page_title="AI-Bot 库存控制台",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.session_state._page_config_set = True


def _hydrate_session_from_settings() -> dict:
    """从后台 /api/settings 把所有持久化设定灌入 st.session_state。"""
    settings = fetch_settings() or {}
    conn = settings.get("connection") or {}
    html = settings.get("htmlServer") or {}
    ui = settings.get("ui") or {}

    st.session_state.setdefault("host", conn.get("host", "localhost"))
    st.session_state.setdefault("port", int(conn.get("port", 25565)))
    st.session_state.setdefault("username", conn.get("username", "InvBot"))
    st.session_state.setdefault("version", conn.get("version", ""))
    st.session_state.setdefault("auth", conn.get("auth", "offline"))

    # 即使是已有的 key，也用最新设定覆盖（这样从设定页存档后立即生效）
    if conn:
        st.session_state["host"] = conn.get("host", st.session_state["host"])
        st.session_state["port"] = int(conn.get("port", st.session_state["port"]))
        st.session_state["username"] = conn.get("username", st.session_state["username"])
        st.session_state["version"] = conn.get("version", st.session_state["version"])
        st.session_state["auth"] = conn.get("auth", st.session_state["auth"])

    st.session_state["html_port"] = int(html.get("port", 8000))
    st.session_state["html_server_enabled"] = bool(html.get("enabled", False))
    st.session_state["auto_refresh"] = bool(ui.get("autoRefresh", False))
    return settings


def _autostart_html_server(settings: dict) -> None:
    """若设定里 htmlServer.enabled=True 就帮使用者把伺服器自动开起来。"""
    html = settings.get("htmlServer") or {}
    if not html.get("enabled"):
        return
    if html_is_running():
        return
    if st.session_state.get("_html_autostart_attempted"):
        return
    st.session_state["_html_autostart_attempted"] = True
    try:
        start_default(port=int(html.get("port", 8000)))
    except OSError:
        # port 被占用时静默；使用者可以从设定页重新启动
        pass


def run() -> None:
    _set_page_config_once()
    apply_styles()

    settings = _hydrate_session_from_settings()
    _autostart_html_server(settings)

    status = api_get("/bot/status")
    if status.get("_error"):
        st.error(f"无法连线 API：{status['_error']}")
        st.stop()

    is_online = render_sidebar(status)

    tabs = st.tabs(["📦 仓库", "🗺️ 箱子管理", "⚙️ 设定", "🧰 其他", "📊 日志"])
    with tabs[0]:
        tab_inventory(is_online)
    with tabs[1]:
        tab_chests(is_online)
    with tabs[2]:
        tab_settings()
    with tabs[3]:
        tab_misc(is_online)
    with tabs[4]:
        tab_logs()

    if st.session_state.get("auto_refresh") and is_online:
        time.sleep(3)
        st.rerun()


if __name__ == "__main__":
    run()
