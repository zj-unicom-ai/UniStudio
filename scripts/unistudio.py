#!/usr/bin/env python3
"""UniStudio local AI workflow CLI. All commands return JSON."""
import argparse
import io
import json
import os
import subprocess
import sys
import urllib.request
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from task_service import tasks
from task_service.config import ROOT, catalog, load_config, publishers, select
from task_service.environment import check_environment, tts_headers


def synthesize(text_file, output):
    cfg = load_config()["tts"]
    if not cfg.get("model") or not cfg.get("voice"):
        raise ValueError("先配置 TTS model 与 voice；不可沿用作者的私人声线")
    text = Path(text_file).read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError("配音文案为空")
    target = tasks.local_path(output)
    if not target.parent.is_dir():
        target.parent.mkdir(parents=True)
    body = json.dumps({"model": cfg["model"], "voice": cfg["voice"], "input": text,
                       "response_format": "wav"}, ensure_ascii=False).encode()
    req = urllib.request.Request(cfg["base_url"].rstrip("/") + cfg.get("speech_path", "/v1/audio/speech"),
                                 data=body, headers={"Content-Type": "application/json", **tts_headers(cfg)}, method="POST")
    with urllib.request.urlopen(req, timeout=600) as response:
        audio = response.read()
    with wave.open(io.BytesIO(audio), "rb") as wav:
        duration = wav.getnframes() / wav.getframerate()
        if duration <= 0:
            raise ValueError("TTS 返回空音频")
        rate, channels = wav.getframerate(), wav.getnchannels()
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_bytes(audio)
    temporary.replace(target)
    return {"path": tasks.relative(target), "duration_s": round(duration, 3), "sample_rate": rate, "channels": channels}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    doctor = sub.add_parser("doctor", help="只读检查制作环境；不会安装或启动 TTS/HyperFrames")
    doctor.add_argument("--template")
    sub.add_parser("templates")
    sub.add_parser("publishers")
    new = sub.add_parser("new", help="环境通过后复制模板并登记制作任务")
    new.add_argument("--template", required=True)
    new.add_argument("--name", required=True)
    new.add_argument("--brief", required=True)
    new.add_argument("--platform", default="")
    ready = sub.add_parser("ready", help="核验成片并登记为待发布；相同任务可幂等更新")
    ready.add_argument("--id", required=True)
    ready.add_argument("--video", required=True)
    ready.add_argument("--cover", required=True)
    ready.add_argument("--title", required=True)
    ready.add_argument("--description", required=True)
    ready.add_argument("--topics", nargs="*", default=[])
    ready.add_argument("--review-note", required=True)
    ls = sub.add_parser("list")
    ls.add_argument("--status", choices=tasks.STATUSES)
    show = sub.add_parser("show")
    show.add_argument("--id", required=True)
    claim = sub.add_parser("claim", help="领取一条待发布任务；仅当前命令返回凭证")
    claim.add_argument("--id", required=True)
    claim.add_argument("--platform", required=True)
    done = sub.add_parser("complete", help="凭领取凭证回写平台实况")
    done.add_argument("--id", required=True)
    done.add_argument("--token", required=True)
    done.add_argument("--status", required=True)
    done.add_argument("--note", required=True)
    done.add_argument("--evidence", required=True)
    done.add_argument("--post-url", default="")
    failed = sub.add_parser("production-failed")
    failed.add_argument("--id", required=True)
    failed.add_argument("--note", required=True)
    reconcile = sub.add_parser("reconcile", help="中断或旧记录的显式平台核验；只有证实未提交才能恢复 ready")
    reconcile.add_argument("--id", required=True)
    reconcile.add_argument("--status", required=True)
    reconcile.add_argument("--note", required=True)
    reconcile.add_argument("--evidence", required=True)
    tts = sub.add_parser("tts", help="使用已配置的 OpenAI-compatible TTS 生成分段 WAV")
    tts.add_argument("--text-file", required=True)
    tts.add_argument("--output", required=True)
    legacy = sub.add_parser("import-legacy", help="显式导入旧看板 JSON，不更改旧数据")
    legacy.add_argument("--source", required=True)
    args = parser.parse_args()
    try:
        if args.command == "doctor":
            result = check_environment(args.template)
        elif args.command == "templates":
            result = catalog()
        elif args.command == "publishers":
            result = publishers()
        elif args.command == "new":
            report = check_environment(args.template)
            if not report["ok"]:
                print(json.dumps(report, ensure_ascii=False, indent=2))
                return 1
            result = tasks.create(args.template, args.name, args.brief, args.platform)
        elif args.command == "ready":
            result = tasks.ready(args.id, args.video, args.cover, args.title, args.description, args.topics, args.review_note)
        elif args.command == "list":
            result = {"records": tasks.list_tasks(args.status)}
        elif args.command == "show":
            with tasks.database() as con:
                result = tasks.public(tasks.find(con, args.id))
        elif args.command == "claim":
            publisher = select(publishers(), args.platform)
            if not (ROOT / publisher["skill"]).is_file():
                raise ValueError("发布 Skill 文件不存在，不能领取任务")
            cfg = load_config().get("publishers", {}).get(args.platform, {})
            result = tasks.claim(args.id, args.platform, cfg.get("account", ""))
        elif args.command == "complete":
            result = tasks.complete(args.id, args.token, args.status, args.note, args.evidence, args.post_url)
        elif args.command == "production-failed":
            result = tasks.production_failed(args.id, args.note)
        elif args.command == "reconcile":
            result = tasks.reconcile(args.id, args.status, args.note, args.evidence)
        elif args.command == "tts":
            result = synthesize(args.text_file, args.output)
        else:
            result = tasks.import_legacy(args.source)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return int(args.command == "doctor" and not result["ok"])
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError, wave.Error) as exc:
        # Do not print provider response bodies, URLs or command arguments containing credentials.
        message = str(exc) if isinstance(exc, ValueError) else f"{type(exc).__name__}：操作失败，请检查配置、文件和服务状态"
        print(json.dumps({"ok": False, "error": message}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
