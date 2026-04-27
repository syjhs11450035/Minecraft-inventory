"""HTTP 客户端：和 Node API server 沟通的所有函式都集中在这。"""

from __future__ import annotations

import os
from typing import Any

import requests

API_BASE = os.environ.get("API_BASE", "http://localhost:80/api")


def _wrap_error(r: requests.Response) -> dict[str, Any]:
    try:
        return {"_error": r.json().get("error", r.text)}
    except Exception:
        return {"_error": f"HTTP {r.status_code}: {r.text[:200]}"}


def api_get(path: str, **kwargs) -> dict[str, Any]:
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=15, **kwargs)
        if r.status_code >= 400:
            return _wrap_error(r)
        return r.json()
    except Exception as e:
        return {"_error": str(e)}


def api_post(path: str, json: dict | None = None) -> dict[str, Any]:
    try:
        r = requests.post(f"{API_BASE}{path}", json=json or {}, timeout=60)
        if r.status_code >= 400:
            return _wrap_error(r)
        return r.json()
    except Exception as e:
        return {"_error": str(e)}


def api_patch(path: str, json: dict | None = None) -> dict[str, Any]:
    try:
        r = requests.patch(f"{API_BASE}{path}", json=json or {}, timeout=15)
        if r.status_code >= 400:
            return _wrap_error(r)
        return r.json()
    except Exception as e:
        return {"_error": str(e)}


def api_delete(path: str) -> dict[str, Any]:
    try:
        r = requests.delete(f"{API_BASE}{path}", timeout=15)
        if r.status_code >= 400:
            return {"_error": r.text}
        return r.json()
    except Exception as e:
        return {"_error": str(e)}


# ---- 区域辅助 ----
def fetch_areas() -> list[dict]:
    data = api_get("/areas")
    if data.get("_error"):
        return []
    return data.get("areas", [])


# ---- 设定（持久化在后台 JSON 档） ----
def fetch_settings() -> dict:
    data = api_get("/settings")
    if data.get("_error"):
        return {}
    return data


def update_settings(patch: dict) -> dict:
    return api_patch("/settings", patch)


def area_select_options(areas: list[dict]) -> list[tuple[str, int | None]]:
    """返回 [(显示名, area_id 或 None)]，含「其他 / 未分类」选项。"""
    opts: list[tuple[str, int | None]] = [("📁 其他（未分类）", None)]
    for a in areas:
        opts.append((f"📦 {a['name']}", a["id"]))
    return opts
