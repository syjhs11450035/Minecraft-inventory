"""Replit 工作流的 Streamlit 入口（薄壳）。

真正的程式码都在专案根的 main/ 资料夹底下。
此档案只是 add sys.path 后呼叫 main.main.run()，让 Replit 平台
绑定的 streamlit 工作流可以正常启动。
"""

from __future__ import annotations

import sys
from pathlib import Path

# 把专案根目录加进 sys.path，才找得到 main 套件
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from main.main import run  # noqa: E402

run()
