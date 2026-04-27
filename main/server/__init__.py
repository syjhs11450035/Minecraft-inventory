"""可切換的本地 HTTP 靜態檔伺服器（serving /html）。

主要由 `main/py/main.py` 控制是否啟動。
"""

from .http_server import (
    HtmlServer,
    get_default_server,
    is_running,
    start_default,
    stop_default,
    server_url,
)

__all__ = [
    "HtmlServer",
    "get_default_server",
    "is_running",
    "start_default",
    "stop_default",
    "server_url",
]
