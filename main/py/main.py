"""核心进入点：组合所有模块、设定页面、画 sidebar 与 tabs。"""

from __future__ import annotations

import time

import streamlit as st

from main.py.ui.api import api_get
from main.py.ui.sidebar import render_sidebar
from main.py.ui.styles import apply_styles
from main.py.ui.tabs.chests import tab_chests
from main.py.ui.tabs.inventory import tab_inventory
from main.py.ui.tabs.logs import tab_logs
from main.py.ui.tabs.misc import tab_misc
from main.py.ui.tabs.settings import tab_settings


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


def _init_session_defaults() -> None:
    st.session_state.setdefault("host", "localhost")
    st.session_state.setdefault("port", 25565)
    st.session_state.setdefault("username", "InvBot")
    st.session_state.setdefault("version", "")
    st.session_state.setdefault("auth", "offline")


def run() -> None:
    _set_page_config_once()
    apply_styles()
    _init_session_defaults()

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
