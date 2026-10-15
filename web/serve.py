#!/usr/bin/env python3
"""自媒体数字员工平台 · 本地查看服务

以项目根目录为站点根启动一个纯标准库 HTTP 服务：
- 访问 http://127.0.0.1:8610/ 进入平台主页（web/index.html）
- 模板预览图、样片、README 等按原仓库路径直接访问
- /api/* 默认读取仓库 pipeline/ 源码，数据存到 productions/state/tasks.db
- /projects/* 提供交付媒体；--pipeline 可兼容旧上游服务
- 默认自动打开浏览器；加 --no-open 可关闭

用法：
    python3 web/serve.py                        # 默认端口 8610
    python3 web/serve.py --port 9000
    python3 web/serve.py --pipeline 127.0.0.1:8899
    python3 web/serve.py --no-open
"""

import argparse
import json
import socketserver
import threading
import urllib.error
import urllib.request
import webbrowser
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # 项目根目录
sys.path.insert(0, str(ROOT))
from pipeline.http import Handler as LocalHandler
HOST = "127.0.0.1"
DEFAULT_PORT = 8610

# 任务和状态统一由当前项目服务管理；旧服务只作为本地媒体文件的兼容代理。
PROXY_PREFIXES = ("/projects/",)


class Handler(LocalHandler):
    pipeline_upstream = None  # 由 main() 注入

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path in ("/", ""):
            self.send_response(302)
            self.send_header("Location", "/web/index.html")
            self.end_headers()
            return
        if self.pipeline_upstream and self.path.startswith(PROXY_PREFIXES):
            self._proxy(self.path)
            return
        return super().do_GET()

    def do_HEAD(self):
        if self.pipeline_upstream and self.path.startswith(PROXY_PREFIXES):
            self._proxy(self.path)
            return
        return super().do_HEAD()

    def _proxy(self, path: str) -> None:
        base = self.pipeline_upstream.strip().rstrip("/")
        if not base.startswith(("http://", "https://")):
            base = "http://" + base
        upstream = base + path
        try:
            req = urllib.request.Request(upstream, method=self.command)
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
                if self.command != "HEAD":
                    self.wfile.write(body)
                return
            with up:
                self.send_response(up.status)
                for h in ("Content-Type", "Content-Length", "Content-Range", "Accept-Ranges"):
                    v = up.headers.get(h)
                    if v:
                        self.send_header(h, v)
                self.end_headers()
                if self.command == "HEAD":
                    return
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
            if self.command != "HEAD":
                self.wfile.write(payload)

    def log_message(self, fmt, *args):
        print(f"[server] {self.address_string()} {fmt % args}")


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


def main() -> None:
    parser = argparse.ArgumentParser(description="自媒体数字员工平台 · 本地查看服务")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"监听端口（默认 {DEFAULT_PORT}）")
    parser.add_argument("--pipeline", default=None, help="可选：代理到已有任务服务；默认使用仓库内置服务")
    parser.add_argument("--no-open", action="store_true", help="启动后不自动打开浏览器")
    args = parser.parse_args()

    Handler.pipeline_upstream = args.pipeline
    url = f"http://{HOST}:{args.port}/"
    with Server((HOST, args.port), Handler) as httpd:
        print(f"自媒体数字员工平台已启动：{url}")
        print(f"站点根目录：{ROOT}")
        print(f"任务数据：{args.pipeline or '内置服务 · productions/state/tasks.db'}")
        print("Ctrl+C 停止")
        if not args.no_open:
            threading.Timer(0.6, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n已停止。")


if __name__ == "__main__":
    main()
