#!/usr/bin/env python3
"""自媒体数字员工平台 · 本地查看服务

以项目根目录为站点根启动一个纯标准库 HTTP 服务：
- 访问 http://127.0.0.1:8610/ 进入平台主页（web/index.html）
- 模板预览图、样片、README 等按原仓库路径直接访问
- /api/* 与 /projects/* 反向代理到任务看板服务（默认 127.0.0.1:8898），
  让平台内的「任务看板 / 自动发布 / 主页统计」读取真实数据（platform.db）
- 默认自动打开浏览器；加 --no-open 可关闭

用法：
    python3 web/serve.py                        # 默认端口 8610
    python3 web/serve.py --port 9000
    python3 web/serve.py --pipeline 127.0.0.1:8899
    python3 web/serve.py --no-open
"""

import argparse
import http.server
import json
import socketserver
import threading
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # 项目根目录
HOST = "127.0.0.1"
DEFAULT_PORT = 8610
DEFAULT_PIPELINE = "127.0.0.1:8898"

# 需要代理到任务看板服务的前缀：统计数据、记录接口、成片与封面媒体
PROXY_PREFIXES = ("/api/", "/projects/")


class Handler(http.server.SimpleHTTPRequestHandler):
    pipeline_upstream = None  # 由 main() 注入

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if self.path in ("/", ""):
            self.send_response(302)
            self.send_header("Location", "/web/index.html")
            self.end_headers()
            return
        if self.path.startswith(PROXY_PREFIXES):
            self._proxy(self.path)
            return
        return super().do_GET()

    def _proxy(self, path: str) -> None:
        base = self.pipeline_upstream.strip().rstrip("/")
        if not base.startswith(("http://", "https://")):
            base = "http://" + base
        upstream = base + path
        try:
            req = urllib.request.Request(upstream, method="GET")
            rng = self.headers.get("Range")
            if rng:
                req.add_header("Range", rng)
            try:
                up = urllib.request.urlopen(req, timeout=30)
            except urllib.error.HTTPError as he:
                # 上游 4xx/5xx：原样转发状态与响应体
                body = he.read()
                self.send_response(he.code)
                ct = he.headers.get("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Type", ct)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            with up:
                self.send_response(up.status)
                for h in ("Content-Type", "Content-Length", "Content-Range", "Accept-Ranges"):
                    v = up.headers.get(h)
                    if v:
                        self.send_header(h, v)
                self.end_headers()
                while True:
                    chunk = up.read(65536)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
        except urllib.error.URLError as exc:
            self.send_response(502)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            payload = json.dumps(
                {"error": "pipeline_unavailable", "detail": str(exc.reason)}
            ).encode("utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    def log_message(self, fmt, *args):
        print(f"[server] {self.address_string()} {fmt % args}")


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


def main() -> None:
    parser = argparse.ArgumentParser(description="自媒体数字员工平台 · 本地查看服务")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"监听端口（默认 {DEFAULT_PORT}）")
    parser.add_argument("--pipeline", default=DEFAULT_PIPELINE, help=f"任务看板上游服务地址（默认 {DEFAULT_PIPELINE}）")
    parser.add_argument("--no-open", action="store_true", help="启动后不自动打开浏览器")
    args = parser.parse_args()

    Handler.pipeline_upstream = args.pipeline
    url = f"http://{HOST}:{args.port}/"
    with Server((HOST, args.port), Handler) as httpd:
        print(f"自媒体数字员工平台已启动：{url}")
        print(f"站点根目录：{ROOT}")
        print(f"任务数据上游：{args.pipeline}（/api/*、/projects/* 反向代理）")
        print("Ctrl+C 停止")
        if not args.no_open:
            threading.Timer(0.6, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n已停止。")


if __name__ == "__main__":
    main()
