"""Read-only dashboard API and restricted, Range-capable media serving."""
import json
import re
from http.server import SimpleHTTPRequestHandler
from urllib.parse import unquote, urlsplit

from .config import PROJECTS, ROOT, catalog_with_ages, publishers
from .tasks import list_tasks, set_board_status, stats


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def list_directory(self, path):
        self.send_error(403, "Directory listing disabled")
        return None

    def json_response(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def send_head(self):
        self._remaining = None
        path = urlsplit(self.path).path
        if path == "/":
            self.send_response(302)
            self.send_header("Location", "/web/index.html")
            self.end_headers()
            return None
        if path.startswith("/api/"):
            try:
                if path == "/api/stats":
                    payload = stats()
                elif path == "/api/records":
                    payload = {"records": list_tasks()}
                elif path == "/api/templates":
                    payload = {"templates": catalog_with_ages()}
                elif path == "/api/publishers":
                    payload = {"publishers": publishers()}
                elif path == "/api/health":
                    payload = {"ok": True, "service": "unistudio"}
                else:
                    self.json_response(404, {"error": "unknown_api"})
                    return None
                self.json_response(200, payload)
            except Exception:
                self.json_response(500, {"error": "task_service_error"})
            return None
        if path.startswith("/projects/"):
            target = (PROJECTS / unquote(path[len("/projects/"):])).resolve()
            allowed_root = PROJECTS.resolve()
            # Only public delivery media, never briefs, evidence or local credentials.
            allowed = "deliver" in target.relative_to(allowed_root).parts if target.is_relative_to(allowed_root) else False
            allowed = allowed and target.suffix.lower() in (".mp4", ".png", ".jpg", ".jpeg", ".webm")
        elif path.startswith("/templates/"):
            target = (ROOT / unquote(path).lstrip("/")).resolve()
            allowed_root = (ROOT / "templates").resolve()
            allowed = target.is_relative_to(allowed_root)
        elif path in ("/web/index.html", "/web/"):
            target = ROOT / "web/index.html"
            allowed_root, allowed = ROOT / "web", True
        else:
            self.send_error(404)
            return None
        if not allowed or any(p.startswith(".") for p in target.relative_to(allowed_root).parts):
            self.send_error(403)
            return None
        if not target.is_file():
            self.send_error(404)
            return None
        size = target.stat().st_size
        start, end, status = 0, size - 1, 200
        rng = self.headers.get("Range")
        if rng:
            match = re.fullmatch(r"bytes=(\d*)-(\d*)", rng)
            if not match or not any(match.groups()) or size == 0:
                return self.unsatisfied_range(size)
            left, right = match.groups()
            if left:
                start, end = int(left), min(int(right), size - 1) if right else size - 1
            else:
                start = max(0, size - int(right))
            if start > end or start >= size:
                return self.unsatisfied_range(size)
            status = 206
        fh = target.open("rb")
        fh.seek(start)
        self._remaining = end - start + 1
        self.send_response(status)
        self.send_header("Content-Type", self.guess_type(str(target)))
        self.send_header("Content-Length", str(self._remaining))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-store")
        if status == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        return fh

    def do_POST(self):
        path = urlsplit(self.path).path
        match = re.fullmatch(r"/api/records/([^/]+)/status", path)
        if not match:
            self.json_response(404, {"error": "unknown_api"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size < 1 or size > 4096:
                self.json_response(400, {"error": "invalid_request"})
                return
            body = json.loads(self.rfile.read(size))
            if not isinstance(body, dict) or not isinstance(body.get("status"), str):
                self.json_response(400, {"error": "invalid_request"})
                return
            record = set_board_status(unquote(match.group(1)), body["status"])
            self.json_response(200, {"record": record})
        except (ValueError, json.JSONDecodeError) as exc:
            self.json_response(400, {"error": str(exc)})
        except Exception:
            self.json_response(500, {"error": "task_service_error"})

    def unsatisfied_range(self, size):
        self.send_response(416)
        self.send_header("Content-Range", f"bytes */{size}")
        self.send_header("Content-Length", "0")
        self.end_headers()
        return None

    def copyfile(self, source, outputfile):
        left = self._remaining
        try:
            while left > 0:
                chunk = source.read(min(65536, left))
                if not chunk:
                    break
                outputfile.write(chunk)
                left -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass
