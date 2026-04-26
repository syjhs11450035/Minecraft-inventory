"""数量换算（箱-组-个）与状态徽章 HTML。"""

from __future__ import annotations


def split_box_stack_single(count: int, stack_size: int) -> tuple[int, int, int]:
    """把数量换算为 (箱, 组, 个)；1 箱 = 27 组。"""
    per_box = stack_size * 27
    boxes = count // per_box
    rem = count - boxes * per_box
    stacks = rem // stack_size
    singles = rem - stacks * stack_size
    return boxes, stacks, singles


def fmt_box_stack_single(boxes: int, stacks: int, singles: int) -> str:
    parts = []
    if boxes > 0:
        parts.append(f"{boxes} 箱")
    if stacks > 0:
        parts.append(f"{stacks} 组")
    if singles > 0 or not parts:
        parts.append(f"{singles} 个")
    return " - ".join(parts)


def status_pill(status: dict) -> str:
    s = status.get("status", "disconnected")
    if s == "spawned":
        return '<span class="status-pill status-online">🟢 已上线</span>'
    if s in ("connecting", "connected"):
        return '<span class="status-pill status-busy">🟡 连线中</span>'
    if s == "error":
        return '<span class="status-pill status-error">🔴 错误</span>'
    return '<span class="status-pill status-offline">⚪ 已离线</span>'
