"""Repository-relative configuration; credentials are read only from environment."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCTIONS = ROOT / "productions"
PROJECTS = PRODUCTIONS / "projects"
STATE = PRODUCTIONS / "state"


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


def publishers():
    return json.loads((ROOT / "skills/publishers.json").read_text(encoding="utf-8"))


def select(items, item_id):
    for item in items:
        if item["id"] == item_id:
            return item
    raise ValueError(f"未登记的标识：{item_id}")
