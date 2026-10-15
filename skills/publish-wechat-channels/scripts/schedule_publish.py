#!/usr/bin/env python3
"""Read-only schedule preflight. Browser submission belongs to the publishing Skill."""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from pipeline import tasks
from pipeline.config import load_config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", required=True, help="Exact task ID")
    parser.add_argument("--at", required=True, help="ISO 8601 time including timezone")
    args = parser.parse_args()
    try:
        when = datetime.fromisoformat(args.at)
        if when.tzinfo is None or when <= datetime.now(timezone.utc):
            raise ValueError("排期必须是带时区的未来时间")
        with tasks.database() as con:
            rec = tasks.find(con, args.id)
        if rec["status"] not in ("ready", "publishing"):
            raise ValueError("只为待发布或本次领取的任务准备排期；已提交作品先核验")
        if rec.get("platform_id") not in (None, "", "wechat-channels"):
            raise ValueError("任务指定的是其他平台")
        cfg = load_config().get("publishers", {}).get("wechat-channels", {})
        if not cfg.get("account"):
            raise ValueError("须先配置目标视频号账号")
        plan = {"mode": "plan_only", "id": rec["id"], "account": cfg["account"],
                "at": when.isoformat(), "title": rec["short_title"],
                "description": rec["description"], "topics": rec.get("topics", []),
                "collection": cfg.get("collection", ""), "original": cfg.get("original", False),
                "video": str(tasks.local_path(rec["video"])), "cover": str(tasks.local_path(rec["cover"])),
                "next": "按 SKILL.md 操作浏览器；回读完整排期后使用 complete 回写 scheduled"}
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
