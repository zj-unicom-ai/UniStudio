"""SQLite task lifecycle shared by the CLI and dashboard (Python standard library)."""
import hashlib
import json
import re
import shutil
import sqlite3
import subprocess
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from .config import PROJECTS, ROOT, STATE, catalog, publishers, select

STATUSES = ("producing", "production_failed", "ready", "publishing", "draft_saved",
            "scheduled", "platform_pending", "published", "failed", "needs_human", "held")


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@contextmanager
def database():
    STATE.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(STATE / "tasks.db", timeout=15)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, data TEXT NOT NULL)")
    try:
        con.execute("BEGIN IMMEDIATE")
        yield con
        con.commit()
    except BaseException:
        con.rollback()
        raise
    finally:
        con.close()


def rows(con):
    return [json.loads(row[0]) for row in con.execute("SELECT data FROM tasks ORDER BY rowid")]


def find(con, task_id):
    row = con.execute("SELECT data FROM tasks WHERE id=?", (task_id,)).fetchone()
    if row is None:
        raise ValueError(f"任务不存在：{task_id}")
    return json.loads(row[0])


def save(con, rec, event, note=""):
    rec["updated_at"] = now()
    rec["last_note"] = note
    rec.setdefault("log", []).append({"at": rec["updated_at"], "event": event, "note": note})
    con.execute("INSERT INTO tasks VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET data=excluded.data",
                (rec["id"], json.dumps(rec, ensure_ascii=False)))
    return rec


def local_path(value, parent=None):
    parent = parent if parent is not None else PROJECTS
    path = Path(value)
    path = (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    if not path.is_relative_to(parent.resolve()):
        raise ValueError(f"路径必须位于 {parent.resolve().relative_to(ROOT.resolve())} 内")
    return path


def relative(path):
    return str(path.resolve().relative_to(ROOT.resolve()))


def public(rec):
    rec = {k: v for k, v in rec.items() if k != "claim_token"}
    for field in ("video", "cover"):
        value = rec.get(field)
        rec[field + "_url"] = ""
        if value:
            try:
                path = local_path(value)
                rec[field + "_url"] = "/projects/" + quote(str(path.relative_to(PROJECTS.resolve())))
            except ValueError:
                pass
    return rec


def list_tasks(status=None):
    with database() as con:
        return [public(r) for r in rows(con) if not status or r["status"] == status]


def stats():
    records = list_tasks()
    out = {"updated_at": max((r["updated_at"] for r in records), default=None),
           "by_status": {}, "by_platform": {}, "days": []}
    days = {}
    for r in records:
        for group, key in (("by_status", r["status"]), ("by_platform", r.get("platform") or "未指定")):
            out[group][key] = out[group].get(key, 0) + 1
        day = r.get("story_date") or r["created_at"][:10]
        item = days.setdefault(day, {"day": day, "total": 0, "published": 0})
        item["total"] += 1
        item["published"] += int(r["status"] == "published")
    out["days"] = [days[k] for k in sorted(days)[-14:]]
    return out


def create(template_id, name, brief, platform=""):
    template = select(catalog(), template_id)
    if not re.fullmatch(r"[a-zA-Z0-9\u4e00-\u9fff][a-zA-Z0-9\u4e00-\u9fff_-]{0,99}", name):
        raise ValueError("工程名须为 1–100 个中英文、数字、下划线或连字符，不含路径分隔符")
    if platform:
        select(publishers(), platform)
    destination = PROJECTS / name
    source = ROOT / template["path"] / template["project_source"]
    if destination.exists():
        raise ValueError("工程已存在，请使用新名称以免覆盖原作品")
    PROJECTS.mkdir(parents=True, exist_ok=True)
    # Pre-create exclusively: concurrent runs must never merge into the same folder.
    destination.mkdir()
    try:
        shutil.copytree(source, destination, dirs_exist_ok=True, ignore=shutil.ignore_patterns(
            ".git", ".DS_Store", "node_modules", "__pycache__", "*.pyc", ".env*", "*.local.json",
            "out", "renders", "deliver", "snapshots", ".hyperframes", ".transcode-cache",
            ".thumbnails", ".waveform-cache", "preview"))
        (destination / "deliver").mkdir()
        (destination / "UNISTUDIO-BRIEF.md").write_text(
            f"# 本期制作需求\n\n{brief}\n\n模板：{template_id}\n\n"
            "模板中的文案与配音为示例，新内容须替换并核对来源。\n", encoding="utf-8")
        stamp = now()
        rec = {"id": "task-" + uuid.uuid4().hex[:12], "project": name,
               "project_dir": relative(destination), "template": template_id, "brief": brief,
               "platform_id": platform, "platform": select(publishers(), platform)["name"] if platform else "",
               "status": "producing", "created_at": stamp, "story_date": stamp[:10], "attempts": 0}
        with database() as con:
            save(con, rec, "producing", "工程已复制；按模板说明制作，完成后执行 ready 登记成片")
        return public(rec)
    except BaseException:
        shutil.rmtree(destination)
        raise


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def probe(video):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(video)],
                            capture_output=True, text=True, timeout=60, check=True)
    info = json.loads(result.stdout)
    stream = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)
    duration = float(info.get("format", {}).get("duration", 0))
    if not stream or duration <= 0 or not stream.get("width") or not stream.get("height"):
        raise ValueError("成片没有有效视频流或时长")
    return {"duration_s": round(duration, 3), "duration": f"{int(duration)//60}:{int(duration)%60:02d}",
            "resolution": f"{stream['width']}×{stream['height']}",
            "size_mb": round(video.stat().st_size / 1024**2, 2),
            "has_audio": any(s.get("codec_type") == "audio" for s in info.get("streams", []))}


def ready(task_id, video, cover, title, description, topics, review_note):
    if not title.strip() or not description.strip() or not review_note.strip():
        raise ValueError("标题、描述和成片检查说明不能为空")
    with database() as con:
        rec = find(con, task_id)
        if rec["status"] not in ("producing", "production_failed", "ready"):
            raise ValueError("当前状态不能覆盖成片；已领取或提交的任务须先核验")
        deliver = local_path(rec["project_dir"]) / "deliver"
        video, cover = local_path(video, deliver), local_path(cover, deliver)
        if video.suffix.lower() != ".mp4" or not video.is_file() or not video.stat().st_size:
            raise ValueError("成片必须是 deliver/ 中的非空 MP4 文件")
        if cover.suffix.lower() not in (".png", ".jpg", ".jpeg") or not cover.is_file() or not cover.stat().st_size:
            raise ValueError("封面必须是 deliver/ 中的非空 PNG/JPG 文件")
        media = probe(video)
        if not media["has_audio"]:
            raise ValueError("成片没有音轨，请核对配音或 BGM 后再登记")
        rec.update(video=relative(video), cover=relative(cover), short_title=title, description=description,
                   topics=topics, media=media, review_note=review_note, video_sha256=digest(video),
                   cover_sha256=digest(cover), status="ready")
        save(con, rec, "ready", review_note)
        return public(rec)


def set_board_status(task_id, status):
    """Manually classify a finished video as ready or published from the dashboard."""
    if status not in ("ready", "published"):
        raise ValueError("看板状态只能是 ready（待发布）或 published（已发布）")
    with database() as con:
        rec = find(con, task_id)
        if rec["status"] in ("producing", "production_failed", "publishing"):
            raise ValueError("制作中或正在发布的任务不能手动切换状态")
        if not rec.get("video"):
            raise ValueError("该任务没有本机可用的成片，不能修改看板状态")
        video = local_path(rec["video"])
        if not video.is_file() or not video.stat().st_size:
            raise ValueError("成片文件不存在或为空，不能修改看板状态")
        if status == "ready":
            for field in ("video", "cover"):
                value = rec.get(field)
                if not value:
                    raise ValueError("待发布任务必须有成片和封面")
                path = local_path(value)
                expected = rec.get(field + "_sha256")
                if not path.is_file() or not expected or digest(path) != expected:
                    raise ValueError("成片或封面已改变；请重新核验并执行 ready")
        previous = rec["status"]
        rec["status"] = status
        note = f"手动调整看板状态：{previous} → {status}"
        return public(save(con, rec, "status_changed", note))


def claim(task_id, platform, account):
    publisher = select(publishers(), platform)
    if not account.strip():
        raise ValueError("发布目标账号未配置")
    with database() as con:
        rec = find(con, task_id)
        if rec["status"] != "ready":
            raise ValueError("只能领取 ready（待发布）任务；结果不明的提交不得自动重试")
        if rec.get("platform_id") and rec["platform_id"] != platform:
            raise ValueError("目标平台与任务指定的平台不一致")
        if platform == "wechat-channels" and len(rec["short_title"]) > 16:
            raise ValueError("视频号短标题超过 16 字；先修改文案再发布")
        for field in ("video", "cover"):
            if digest(local_path(rec[field])) != rec[field + "_sha256"]:
                raise ValueError("成片或封面已改变，请重新检查并执行 ready")
        fingerprint = (rec["video_sha256"], platform, account)
        for other in rows(con):
            if other["id"] == task_id:
                continue
            if other.get("platform_id") == platform and other["status"] == "publishing":
                raise ValueError(f"该平台有未结束的发布会话：{other['id']}，先回读并收口")
            if (other.get("video_sha256"), other.get("platform_id"), other.get("account")) == fingerprint and other["status"] in (
                    "publishing", "draft_saved", "scheduled", "platform_pending", "published", "needs_human"):
                raise ValueError(f"相同视频已在该账号提交或待核验：{other['id']}")
        rec.update(platform_id=platform, platform=publisher["name"], account=account,
                   status="publishing", claim_token=uuid.uuid4().hex, claimed_at=now(),
                   attempts=rec.get("attempts", 0) + 1)
        save(con, rec, "publishing", "已领取发布会话；提交后须回读平台状态")
        return rec  # Token is returned only to the claiming CLI, never by the public API.


def complete(task_id, token, status, note, evidence, post_url=""):
    if status not in ("published", "platform_pending", "scheduled", "draft_saved", "failed", "needs_human"):
        raise ValueError("无效的发布结果状态")
    proof = local_path(evidence)
    if not proof.is_file() or not proof.stat().st_size:
        raise ValueError("须提供工程内的平台回读记录或截图作为证据")
    if not note.strip():
        raise ValueError("须记录平台实际返回的状态或异常")
    with database() as con:
        rec = find(con, task_id)
        if not token or rec.get("claim_token") != token:
            raise ValueError("领取凭证不匹配，不能覆盖其他发布会话")
        if rec["status"] not in ("publishing", "platform_pending", "scheduled", "draft_saved", "needs_human"):
            raise ValueError("该任务不在可核验的发布会话中")
        local_path(proof, local_path(rec["project_dir"]))
        rec.update(status=status, evidence=relative(proof), verify_note=note, post_url=post_url)
        save(con, rec, status, note)
        return public(rec)


def production_failed(task_id, note):
    with database() as con:
        rec = find(con, task_id)
        if rec["status"] not in ("producing", "production_failed"):
            raise ValueError("只能标记制作阶段的失败")
        rec["status"] = "production_failed"
        return public(save(con, rec, "production_failed", note))


def reconcile(task_id, status, note, evidence):
    """Explicit recovery after inspecting the platform; never automatic lease expiry."""
    if status not in ("ready", "published", "platform_pending", "scheduled", "draft_saved", "failed", "needs_human"):
        raise ValueError("无效的核验状态")
    proof = local_path(evidence)
    if not note.strip() or not proof.is_file() or not proof.stat().st_size:
        raise ValueError("恢复操作须附平台核验说明与非空证据文件")
    with database() as con:
        rec = find(con, task_id)
        if rec["status"] not in ("publishing", "failed", "needs_human", "platform_pending", "scheduled", "draft_saved"):
            raise ValueError("当前状态不需要恢复核验")
        local_path(proof, local_path(rec["project_dir"]))
        if status == "ready":
            for field in ("video", "cover"):
                if digest(local_path(rec[field])) != rec[field + "_sha256"]:
                    raise ValueError("文件已改变，不能恢复为待发布")
        rec.pop("claim_token", None)
        rec.update(status=status, evidence=relative(proof), verify_note=note)
        return public(save(con, rec, "reconciled", note))


def import_legacy(source):
    """Explicit, idempotent import; never modify the old DB or its mirror."""
    data = json.loads(Path(source).read_text(encoding="utf-8"))
    imported = 0
    with database() as con:
        for old in data["records"]:
            if con.execute("SELECT 1 FROM tasks WHERE id=?", (old["id"],)).fetchone():
                continue
            rec = dict(old)
            rec.pop("claim_token", None)
            rec.setdefault("created_at", now())
            for field in ("video", "cover"):
                if rec.get(field):
                    try:
                        path = local_path(rec[field])
                        rec[field] = relative(path)
                        if path.is_file():
                            rec[field + "_sha256"] = digest(path)
                    except ValueError:
                        rec[field] = ""
            rec["project_dir"] = "productions/projects/" + rec["project"]
            rec["platform_id"] = "wechat-channels"
            rec["platform"] = "视频号"
            # Imported in-flight sessions have no valid local claim; reconcile manually.
            if rec.get("status") not in STATUSES or rec["status"] == "publishing":
                rec["status"] = "needs_human"
            if rec["status"] == "ready" and not all(rec.get(k) for k in ("video", "cover", "video_sha256", "cover_sha256")):
                rec["status"] = "needs_human"
            save(con, rec, "imported", "从旧看板导入；原始数据保持不变")
            imported += 1
    return {"imported": imported}
