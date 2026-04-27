"""Streamlit 全域 CSS 样式。"""

import streamlit as st

_CSS = """
<style>
    section[data-testid="stSidebar"] { background: #0f1419; }
    section[data-testid="stSidebar"] * { color: #e6edf3; }
    .status-pill {
        display: inline-block; padding: 4px 12px; border-radius: 999px;
        font-weight: 600; font-size: 0.95rem;
    }
    .status-online  { background: #16a34a; color: white; }
    .status-busy    { background: #d97706; color: white; }
    .status-offline { background: #4b5563; color: white; }
    .status-error   { background: #dc2626; color: white; }
    .stat-card {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color: white; padding: 14px; border-radius: 12px; text-align:center;
        margin-bottom: 8px;
    }
    .stat-card .label { font-size: 0.8rem; opacity: 0.85; }
    .stat-card .value { font-size: 1.6rem; font-weight: 700; margin-top: 4px;}
    .block-container { padding-top: 3.5rem; }
    div[data-testid="stTabs"] { margin-top: 0.5rem; }
    button[data-baseweb="tab"] { font-size: 1rem !important; padding: 10px 18px !important; }
</style>
"""


def apply_styles() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
