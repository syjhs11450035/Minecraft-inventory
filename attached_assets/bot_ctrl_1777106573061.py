import os
import sys
import subprocess
import time
import json

from utils import BOT_CORE_PATH, BOT_LOG_FILE, BOT_INVENTORY_FILE, BOT_STATUS_FILE, BOT_STOP_SIGNAL_FILE, BOT_COMMAND_FILE, is_process_running

def is_bot_process_running(pid):
    return is_process_running(pid, script_name="bot_core.py")

def start_bot_process():
    """
    啟動 bot_core.py 作為一個獨立的後台進程。
    """
    # 啟動前清理所有舊的數據文件，確保從一個乾淨的狀態開始
    for f in [BOT_LOG_FILE, BOT_INVENTORY_FILE, BOT_STATUS_FILE, BOT_STOP_SIGNAL_FILE, BOT_COMMAND_FILE]:
        if os.path.exists(f):
            os.remove(f)
    
    python_exe = sys.executable # 使用當前 Streamlit 運行的 Python 環境
    try:
        process = subprocess.Popen([python_exe, BOT_CORE_PATH])
        return {"success": True, "pid": process.pid}
    except Exception as e:
        return {"success": False, "message": f"啟動機器人失敗: {e}"}

def stop_bot_process(pid):
    """
    停止機器人進程。
    """
    if not is_bot_process_running(pid):
        return {"success": False, "message": "機器人未運行"}

    # 透過創建一個停止信號文件來通知 bot_core.py 進程自行終止
    with open(BOT_STOP_SIGNAL_FILE, "w") as f:
        f.write("STOP")
    
    # 等待 bot_core.py 進程結束，設定最長等待時間為 10 秒
    start_time = time.time()
    while is_bot_process_running(pid) and (time.time() - start_time < 10):
        time.sleep(0.5)
    
    if is_bot_process_running(pid):
        return {"success": False, "message": "機器人未在預期時間內停止，可能需要手動終止進程。"}
    else:
        # 清理停止信號文件，以防下次啟動時立即停止
        if os.path.exists(BOT_STOP_SIGNAL_FILE):
            os.remove(BOT_STOP_SIGNAL_FILE)
        return {"success": True, "message": "機器人已停止。"}

def trigger_remote_command(command_type, params=None, bot_process_pid=None):
    if not is_bot_process_running(bot_process_pid):
        return {"success": False, "message": "機器人未啟動"}
    command_data = {"command": command_type, "params": params or {}}
    with open(BOT_COMMAND_FILE, "w", encoding="utf-8") as f:
        json.dump(command_data, f, ensure_ascii=False)
    return {"success": True, "command": command_type}