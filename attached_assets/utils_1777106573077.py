import os
import json
import psutil
from pathlib import Path
from datetime import datetime

# --- 檔案路徑定義 ---
# 使用 Pathlib 提升路徑處理的安全性
MAIN_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = MAIN_DIR.parent

CONFIG_PATH = MAIN_DIR / "config.json"
BOT_CORE_PATH = MAIN_DIR / "bot_core.py"
BOT_LOG_FILE = MAIN_DIR / "bot_logs.json"
BOT_INVENTORY_FILE = MAIN_DIR / "bot_inventory.json"
BOT_STATUS_FILE = MAIN_DIR / "bot_status.json"
BOT_STOP_SIGNAL_FILE = MAIN_DIR / "stop_signal.txt"
BOT_COMMAND_FILE = MAIN_DIR / "commands.json"

# --- 物品資訊映射表 ---
ITEM_INFO = {
    "diamond": {"icon": "💎", "name": "鑽石"},
    "cobblestone": {"icon": "🪨", "name": "鵝卵石"},
    "iron_ingot": {"icon": "🥈", "name": "鐵錠"},
    "gold_ingot": {"icon": "🥇", "name": "黃金"},
    "emerald": {"icon": "💚", "name": "綠寶石"},
    "redstone": {"icon": "🔴", "name": "紅石"},
    "coal": {"icon": "⚫", "name": "煤炭"},
    "wood": {"icon": "🪵", "name": "原木"},
    "stone": {"icon": "🧱", "name": "石頭"},
    "dirt": {"icon": "💩", "name": "泥土"},
    "sand": {"icon": "⏳", "name": "沙子"},
    "glass": {"icon": "🥃", "name": "玻璃"},
    "water_bucket": {"icon": "💧", "name": "水桶"},
    "lava_bucket": {"icon": "🔥", "name": "岩漿桶"},
    "bread": {"icon": "🍞", "name": "麵包"},
    "steak": {"icon": "🥩", "name": "牛排"},
    "apple": {"icon": "🍎", "name": "蘋果"},
    "carrot": {"icon": "🥕", "name": "胡蘿蔔"},
    "potato": {"icon": "🥔", "name": "馬鈴薯"},
    "shulker_box_blue": {"icon": "📦", "name": "藍色界標盒"},
    "shulker_box_red": {"icon": "📦", "name": "紅色界標盒"},
    "shulker_box_green": {"icon": "📦", "name": "綠色界標盒"}
}

def load_config():
    """讀取用戶自定義的物品 ID 與分類設定"""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Error loading config.json: JSON decode error. Using default config.")
            return {} # Return empty dict or default structure
    return {
        "server": {"host": "127.0.0.1", "port": 25565, "version": "1.20.1"},
        "ai_config": {"api_key": "", "provider": "Gemini", "enabled": False},
        "chest_areas": [
            {"名稱": "區域 A", "座標範圍": "100,64,-200 到 110,64,-210"},
            {"名稱": "區域 B (L型)", "座標範圍": "自定義座標列表"}
        ],
        "bot_settings": {"username": "AI_Bot_GG", "prefix": "!", "auto_reconnect": True, "bot_core_path": BOT_CORE_PATH},
        "sorting_rules": [
            {"物品": "🪨 鵝卵石", "箱子區域": "區域 A", "模式": "一箱子多物品"},
            {"物品": "💎 鑽石", "箱子區域": "區域 B (L型)", "模式": "一箱子一物品"}
        ]
    }

def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def load_bot_logs():
    if os.path.exists(BOT_LOG_FILE):
        try:
            with open(BOT_LOG_FILE, "r", encoding="utf-8") as f:
                return [log["message"] for log in json.load(f)]
        except json.JSONDecodeError:
            return ["日誌檔案損壞，已重置。"]
    return []

def load_bot_inventory():
    if os.path.exists(BOT_INVENTORY_FILE):
        try:
            with open(BOT_INVENTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def load_bot_status():
    if os.path.exists(BOT_STATUS_FILE):
        try:
            with open(BOT_STATUS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"running": False, "username": "N/A", "coordinates": {"x": 0, "y": 0, "z": 0}, "health": 0, "food": 0, "task": "Error"}
    return {"running": False, "username": "N/A", "coordinates": {"x": 0, "y": 0, "z": 0}, "health": 0, "food": 0, "task": "未啟動"}

def is_process_running(pid, script_name="bot_core.py"):
    if pid is None:
        return False
    try:
        proc = psutil.Process(pid)
        return proc.is_running() and "python" in proc.name().lower() and script_name in " ".join(proc.cmdline())
    except psutil.NoSuchProcess:
        return False

def get_bot_api_status(bot_process_pid):
    status = load_bot_status()
    inventory = load_bot_inventory()
    return {
        "status": "online" if is_process_running(bot_process_pid) else "offline",
        "bot_data": status,
        "inventory_count": len(inventory),
        "last_sync": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }