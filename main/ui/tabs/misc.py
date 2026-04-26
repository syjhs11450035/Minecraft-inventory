"""其他分页：聊天/指令送出。"""

from __future__ import annotations

import streamlit as st

from main.ui.api import api_post


def tab_misc(is_online: bool) -> None:
    with st.container(border=True):
        st.markdown("#### 💬 指令")
        st.caption("送出聊天讯息或斜线指令到伺服器。")
        with st.form("cmd_form", clear_on_submit=True):
            msg = st.text_input(
                "讯息 / 指令",
                placeholder="例：/home 或 你好",
                label_visibility="collapsed",
            )
            sent = st.form_submit_button(
                "📨 送出",
                type="primary",
                use_container_width=True,
                disabled=not is_online,
            )
            if sent and msg.strip():
                res = api_post("/bot/chat", {"message": msg.strip()})
                if res.get("_error"):
                    st.error(res["_error"])
                else:
                    st.toast("讯息已送出", icon="📨")
