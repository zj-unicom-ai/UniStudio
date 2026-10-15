"""Read-only production preflight. Never installs services or synthesizes probe audio."""
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

from .config import ROOT, catalog, load_config, select


def tts_headers(config):
    key_name = config.get("api_key_env", "UNISTUDIO_TTS_API_KEY")
    key = os.environ.get(key_name, "")
    return {"Authorization": "Bearer " + key} if key else {}


def check_environment(template_id=None):
    checks = []

    def add(name, ok, detail):
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    add("python", sys.version_info >= (3, 10), "需要 Python 3.10+")
    for binary in ("node", "npm", "ffmpeg", "ffprobe"):
        add(binary, shutil.which(binary), "已找到" if shutil.which(binary) else "请在当前运行环境安装并加入 PATH")
    if shutil.which("node"):
        try:
            version = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=10, check=True).stdout.strip()
            add("node_version", int(version.lstrip("v").split(".")[0]) >= 22, "需要 Node.js 22+")
        except (OSError, subprocess.SubprocessError, ValueError):
            add("node_version", False, "无法确认 Node.js 版本")
    try:
        config = load_config()
    except (OSError, ValueError) as exc:
        add("config", False, str(exc))
        return {"ok": False, "checks": checks}
    command = config.get("hyperframes_command", ["hyperframes"])
    valid = isinstance(command, list) and command and all(isinstance(x, str) and x for x in command)
    # npx may only inspect an already installed CLI. An environment check must not install it.
    if valid and Path(command[0]).name in ("npx", "npx.cmd"):
        valid = "--no-install" in command
    if not valid:
        add("hyperframes", False, "hyperframes_command 须为命令数组；npx 须带 --no-install，不能在预检时安装")
    else:
        try:
            run = subprocess.run([*command, "--version"], cwd=ROOT, capture_output=True, text=True, timeout=30, check=True)
            version = re.search(r"\d+\.\d+\.\d+", run.stdout)
            add("hyperframes", bool(version), "已响应版本命令" if version else "CLI 未返回版本号")
        except (OSError, subprocess.SubprocessError):
            add("hyperframes", False, "当前环境的 HyperFrames 命令不可用，请先准备服务或调整 hyperframes_command")
    tts = config.get("tts", {})
    base = tts.get("base_url", "").rstrip("/")
    add("tts_config", base.startswith(("http://", "https://")), "填写已有 TTS 服务的 base_url 和 health_path")
    if base.startswith(("http://", "https://")):
        try:
            req = urllib.request.Request(base + tts.get("health_path", "/health"), headers=tts_headers(tts))
            with urllib.request.urlopen(req, timeout=10) as response:
                add("tts_service", response.status == 200, "TTS 健康检查已响应；实际模型和声线仍由首次合成验证")
        except (OSError, ValueError, urllib.error.URLError):
            add("tts_service", False, "TTS 健康检查失败；核对地址、路径、鉴权和服务状态")
    template = select(catalog(), template_id) if template_id else None
    if not template or template["narration"]:
        add("tts_voice", bool(tts.get("voice") and tts.get("model")), "配置当前服务支持且有权使用的 model 与 voice")
    if template:
        source = ROOT / template["path"] / template["project_source"]
        pointers = []
        for path in source.rglob("*"):
            if any(p in ("node_modules", ".git") for p in path.parts):
                continue
            if path.is_file() and path.stat().st_size < 1024:
                if path.read_bytes().startswith(b"version https://git-lfs.github.com/spec/v1"):
                    pointers.append(str(path.relative_to(source)))
        add("template_assets", not pointers, "存在 Git LFS 指针，请先 git lfs pull" if pointers else "模板文件已就位")
    return {"ok": all(c["ok"] for c in checks), "checks": checks}
