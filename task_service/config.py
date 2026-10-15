"""Repository-relative configuration; credentials are read only from environment."""
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCTIONS = ROOT / "productions"
PROJECTS = PRODUCTIONS / "projects"
STATE = PRODUCTIONS / "state"

_ADDED_AT = {}  # 首次入库日期一旦提交就不再变化，按路径缓存成功结果


def load_config():
    path = Path(os.environ.get("UNISTUDIO_CONFIG", ROOT / "unistudio.local.json"))
    if not path.is_absolute():
        path = ROOT / path
    if not path.is_file():
        raise ValueError("缺少配置：复制 config/unistudio.example.json 为 unistudio.local.json 并填写 TTS 和账号。")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("配置文件必须是 JSON 对象")
    return data


def catalog():
    return json.loads((ROOT / "templates/catalog.json").read_text(encoding="utf-8"))


def added_at(path):
    """该模板目录首次提交进仓库的日期（YYYY-MM-DD）；未跟踪或无 git 时返回 None。"""
    if not path:
        return None
    if path in _ADDED_AT:
        return _ADDED_AT[path]
    try:
        result = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%ad",
             "--date=format:%Y-%m-%d", "--", path],
            cwd=ROOT, capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    # git log 由新到旧，最后一行即首次入库；日期不含时区，可安全按字符串比较。
    dates = [line for line in result.stdout.splitlines() if line.strip()]
    value = dates[-1].strip() if dates else None
    if value:
        _ADDED_AT[path] = value
    return value


def catalog_with_ages():
    """catalog() 的展示副本，附带 added_at；不影响 doctor/new 使用的原始目录。"""
    items = catalog()
    for item in items:
        item["added_at"] = added_at(item.get("path", ""))
    return items


def publishers():
    return json.loads((ROOT / "skills/publishers.json").read_text(encoding="utf-8"))


def select(items, item_id):
    for item in items:
        if item["id"] == item_id:
            return item
    raise ValueError(f"未登记的标识：{item_id}")
