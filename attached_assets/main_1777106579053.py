import os
import sys
import subprocess
import json
import time
os.system('cls' if os.name == 'nt' else 'clear')

# --- 環境檢查機制 ---
def ensure_dependencies():
    required = ["streamlit", "pandas", "psutil"]
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            print(f"檢測到缺失套件: {pkg}，正在自動安裝...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

if __name__ == "__main__":
    ensure_dependencies()

import streamlit as st
from utils import BOT_STOP_SIGNAL_FILE, get_bot_api_status
from bot_ctrl import is_bot_process_running
from ui_components import render_sidebar, render_main_tabs

# --- Streamlit 自動啟動器邏輯 ---
# 這個區塊的目的是讓使用者可以直接執行 `python main.py`，而不需要手動輸入 `streamlit run ...`。
# 它會偵測當前環境是否已經在 Streamlit 內部運行。如果不是，它會使用 subprocess 重新啟動自己，
# 但這次會帶上 Streamlit 的啟動指令。
if __name__ == "__main__" and "--st_launcher" not in sys.argv:
    # 清理終端機畫面，提供更清晰的啟動體驗
    # 獲取當前 Python 解釋器的完整路徑，確保使用正確的環境啟動 Streamlit
    python_exe = sys.executable
    # 獲取當前腳本的絕對路徑
    script_path = os.path.abspath(__file__)
    
    # 構建 Streamlit 啟動指令的參數列表。
    # 使用列表形式可以避免 Shell 處理路徑中空格和特殊字元時的語法錯誤。
    # `--` 後面的 `--st_launcher` 是一個自定義標記，用於告訴重新啟動的 Streamlit 進程，
    # 它已經是由這個自動啟動器啟動的，避免無限遞迴。
    command = [python_exe, "-m", "streamlit", "run", script_path, "--", "--st_launcher"]
    
    print(f"正在啟動 Streamlit 介面，請稍候...")
    print(f"目前執行環境: {python_exe}")
    try:
        # 執行 Streamlit 啟動指令，並等待其完成
        subprocess.run(command)
    except KeyboardInterrupt:
        # 偵測到 Ctrl + C 時，清空畫面並顯示友善提示，避免顯示錯誤追蹤
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n[👋] 偵測到中斷指令，AI-Bot 管理系統已安全關閉。")
    # 退出當前進程，因為 Streamlit 已經在新的進程中啟動
    sys.exit(0)

# --- Streamlit 主應用程式邏輯 ---
def main():
    # 設定 Streamlit 頁面配置，包括標題、佈局和圖標
    st.set_page_config(page_title="AI-Bot 控制台", layout="wide", page_icon="🤖")

    # 初始化 Streamlit 的 Session State。
    # `bot_process_pid` 用於儲存後端機器人進程的 PID，以便追蹤其狀態。
    if 'bot_process_pid' not in st.session_state:
        st.session_state.bot_process_pid = None

    # 檢查後端 bot_core.py 進程的當前運行狀態
    bot_is_running = is_bot_process_running(st.session_state.bot_process_pid)
    
    # 如果 Streamlit 記錄的 PID 存在，但實際進程已停止，則更新 Streamlit 的狀態
    if not bot_is_running and st.session_state.bot_process_pid is not None:
        st.session_state.bot_process_pid = None
        # 清理停止信號文件。這很重要，因為如果 bot_core.py 異常終止，
        # 停止信號文件可能殘留，導致下次啟動時 bot_core.py 立即關閉。
        if os.path.exists(BOT_STOP_SIGNAL_FILE):
            os.remove(BOT_STOP_SIGNAL_FILE)

    # 渲染 UI 元件
    render_sidebar(bot_is_running)
    render_main_tabs(bot_is_running)

    # --- 自動刷新機制 ---
    if bot_is_running:
        time.sleep(2) # 每 2 秒刷新一次
        st.rerun() # 觸發 Streamlit 重新執行腳本以更新數據

if __name__ == "__main__":
    main()# --- API 接口與外部整合 (擴充功能) ---
