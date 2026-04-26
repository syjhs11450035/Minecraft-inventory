"""根目录启动器：让你能从专案根直接跑 `streamlit run main.py`。

实际程式码都在 main/ 资料夹下，此档案只是一个薄薄的入口点。
"""

from __future__ import annotations

import sys
from pathlib import Path

# 确保不论从哪里启动，专案根目录都在 sys.path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from main.main import run  # noqa: E402

run()
