"""簡易 HTTP 靜態檔伺服器（提供 `/html/` 目錄）。

可由 `main/py/main.py`（Streamlit 設定分頁）切換是否啟用。
使用標準函式庫，無第三方相依。
"""

from __future__ import annotations

import os
import socket
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HTML_DIR = PROJECT_ROOT / "html"


class HtmlServer:
    """背景執行緒中跑的靜態檔伺服器。"""

    def __init__(self, port: int = 8000, directory: Path | str = DEFAULT_HTML_DIR) -> None:
        self.port = int(port)
        self.directory = str(directory)
        self._httpd: Optional[ThreadingHTTPServer] = None
        self._thread: Optional[threading.Thread] = None

    @property
    def running(self) -> bool:
        return self._httpd is not None and self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        if self.running:
            return
        # 確保目錄存在
        Path(self.directory).mkdir(parents=True, exist_ok=True)
        handler = partial(SimpleHTTPRequestHandler, directory=self.directory)
        self._httpd = ThreadingHTTPServer(("0.0.0.0", self.port), handler)
        self._thread = threading.Thread(
            target=self._httpd.serve_forever,
            name=f"html-server:{self.port}",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        if self._httpd is not None:
            try:
                self._httpd.shutdown()
                self._httpd.server_close()
            except OSError:
                pass
        self._httpd = None
        self._thread = None


_default: Optional[HtmlServer] = None
_lock = threading.Lock()


def get_default_server() -> Optional[HtmlServer]:
    return _default


def is_running() -> bool:
    return _default is not None and _default.running


def start_default(port: int = 8000, directory: Path | str = DEFAULT_HTML_DIR) -> HtmlServer:
    """啟動預設靜態伺服器；若已啟動且 port/dir 變了，重啟。"""
    global _default
    with _lock:
        if _default is not None and _default.running:
            if _default.port == int(port) and _default.directory == str(directory):
                return _default
            _default.stop()
        _default = HtmlServer(port=port, directory=directory)
        _default.start()
        return _default


def stop_default() -> None:
    global _default
    with _lock:
        if _default is not None:
            _default.stop()
        _default = None


def server_url() -> Optional[str]:
    """回傳本機可用的 URL（純粹示範，部署環境會以 reverse proxy 暴露）。"""
    if _default is None or not _default.running:
        return None
    host = os.environ.get("REPLIT_DEV_DOMAIN") or _detect_host()
    return f"http://{host}:{_default.port}"


def _detect_host() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        host = s.getsockname()[0]
        s.close()
        return host
    except OSError:
        return "localhost"
