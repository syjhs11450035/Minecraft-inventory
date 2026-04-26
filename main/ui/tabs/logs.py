"""日志分页。"""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from main.ui.api import api_delete, api_get


def tab_logs() -> None:
    cc1, _ = st.columns([1, 5])
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
    with st.container(border=True, height=500):
        st.code(log_text, language="bash")
