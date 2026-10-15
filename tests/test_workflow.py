"""Lifecycle and HTTP integration tests; fixtures never contact TTS or publishers."""
import io
import contextlib
import json
import shutil
import subprocess
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
import wave
from concurrent.futures import ThreadPoolExecutor
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from task_service import tasks
from task_service import config
from task_service.environment import check_environment
from task_service.http import Handler
from scripts import unistudio


class WorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            raise unittest.SkipTest("Install ffmpeg/ffprobe to run lifecycle integration tests")
        cls.media_dir = tempfile.TemporaryDirectory()
        cls.movie = Path(cls.media_dir.name) / "fixture.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=c=blue:s=160x90:d=1",
                        "-f", "lavfi", "-i", "sine=frequency=440:duration=1", "-c:v", "libx264",
                        "-c:a", "aac", "-shortest", str(cls.movie)], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.media_dir.cleanup()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.projects = self.root / "productions/projects"
        self.source = self.root / "templates/demo"
        self.source.mkdir(parents=True)
        (self.root / "skills").mkdir()
        (self.root / "skills/publishers.json").write_text(json.dumps([
            {"id": "wechat-channels", "name": "视频号"}]))
        (self.source / "index.html").write_text("original template")
        (self.source / ".env").write_text("private")
        (self.source / "renders").mkdir()
        (self.source / "renders/old.mp4").write_bytes(b"old")
        template = [{"id": "demo", "path": "templates/demo", "project_source": ".", "narration": False}]
        for target, value in (("task_service.config.ROOT", self.root), ("task_service.tasks.ROOT", self.root),
                              ("task_service.tasks.PROJECTS", self.projects),
                              ("task_service.tasks.STATE", self.root / "productions/state"),
                              ("task_service.tasks.catalog", lambda: template),
                              ("task_service.http.ROOT", self.root), ("task_service.http.PROJECTS", self.projects)):
            mock = patch(target, value)
            mock.start()
            self.addCleanup(mock.stop)

    def create_ready(self, name="episode"):
        rec = tasks.create("demo", name, "This episode's own brief")
        deliver = self.projects / name / "deliver"
        shutil.copyfile(self.movie, deliver / "video.mp4")
        # An actual tiny PNG fixture rather than an external image or user asset.
        import base64
        (deliver / "cover.png").write_bytes(base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+j8N8AAAAASUVORK5CYII="))
        return tasks.ready(rec["id"], deliver / "video.mp4", deliver / "cover.png", "测试短标题", "描述", ["测试"], "fixture review")

    def proof(self, rec):
        path = self.projects / rec["project"] / "publish/verification.txt"
        path.parent.mkdir(exist_ok=True)
        path.write_text("mock platform: this exact record is under review")
        return path

    def test_copy_ready_and_public_api_persistence(self):
        rec = self.create_ready()
        project = self.projects / rec["project"]
        self.assertFalse((project / ".env").exists())
        self.assertFalse((project / "renders").exists())
        self.assertEqual((self.source / "index.html").read_text(), "original template")
        self.assertEqual(tasks.list_tasks("ready")[0]["id"], rec["id"])
        self.assertEqual(rec["media"]["resolution"], "160×90")
        self.assertTrue(rec["media"]["has_audio"])
        self.assertEqual(rec["video_url"], "/projects/episode/deliver/video.mp4")
        self.assertEqual(tasks.stats()["by_status"], {"ready": 1})
        self.assertTrue((self.root / "productions/state/tasks.db").is_file())

    def test_atomic_claim_token_and_no_retry_after_submission(self):
        rec = self.create_ready()

        def attempt():
            try:
                return tasks.claim(rec["id"], "wechat-channels", "My account")
            except ValueError:
                return None

        with ThreadPoolExecutor(max_workers=6) as pool:
            claims = [r for r in pool.map(lambda _: attempt(), range(6)) if r]
        self.assertEqual(len(claims), 1)
        token = claims[0]["claim_token"]
        self.assertNotIn("claim_token", tasks.list_tasks()[0])
        with self.assertRaises(ValueError):
            tasks.complete(rec["id"], "wrong token", "published", "done", self.proof(rec))
        done = tasks.complete(rec["id"], token, "platform_pending", "mock platform: under review", self.proof(rec))
        self.assertEqual(done["status"], "platform_pending")
        with self.assertRaises(ValueError):
            tasks.claim(rec["id"], "wechat-channels", "My account")

    def test_changed_assets_duplicate_content_and_shared_browser(self):
        one, two = self.create_ready("one"), self.create_ready("two")
        claim = tasks.claim(one["id"], "wechat-channels", "account")
        with self.assertRaisesRegex(ValueError, "会话"):
            tasks.claim(two["id"], "wechat-channels", "other account")
        tasks.complete(one["id"], claim["claim_token"], "published", "mock: publicly visible", self.proof(one))
        with self.assertRaisesRegex(ValueError, "相同视频"):
            tasks.claim(two["id"], "wechat-channels", "account")
        (self.projects / "two/deliver/cover.png").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "改变"):
            tasks.claim(two["id"], "wechat-channels", "other account")

    def test_reconcile_invalidates_old_claim(self):
        rec = self.create_ready()
        claimed = tasks.claim(rec["id"], "wechat-channels", "account")
        tasks.reconcile(rec["id"], "ready", "mock platform confirms no submission exists", self.proof(rec))
        second = tasks.claim(rec["id"], "wechat-channels", "account")
        with self.assertRaises(ValueError):
            tasks.complete(rec["id"], claimed["claim_token"], "published", "old worker", self.proof(rec))
        self.assertNotEqual(claimed["claim_token"], second["claim_token"])

    def test_manual_board_status_is_limited_to_two_and_preserves_publish_guard(self):
        rec = self.create_ready()
        published = tasks.set_board_status(rec["id"], "published")
        self.assertEqual(published["status"], "published")
        ready = tasks.set_board_status(rec["id"], "ready")
        self.assertEqual(ready["status"], "ready")
        with self.assertRaisesRegex(ValueError, "只能是 ready"):
            tasks.set_board_status(rec["id"], "platform_pending")
        claimed = tasks.claim(rec["id"], "wechat-channels", "account")
        with self.assertRaisesRegex(ValueError, "正在发布"):
            tasks.set_board_status(rec["id"], "published")
        self.assertEqual(claimed["status"], "publishing")

    def test_dashboard_can_manually_switch_status(self):
        rec = self.create_ready()

        class QuietHandler(Handler):
            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/api/records/{rec['id']}/status",
            data=json.dumps({"status": "published"}).encode(),
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(request) as response:
            updated = json.loads(response.read())["record"]
        self.assertEqual(updated["status"], "published")
        bad_request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/api/records/{rec['id']}/status",
            data=json.dumps({"status": "platform_pending"}).encode(),
            headers={"Content-Type": "application/json"}, method="POST")
        with self.assertRaises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(bad_request)
        self.assertEqual(error.exception.code, 400)

    def test_paths_and_legacy_import_are_bounded_and_idempotent(self):
        with self.assertRaises(ValueError):
            tasks.create("demo", "../escape", "brief")
        with self.assertRaises(ValueError):
            tasks.local_path(self.root / "private.mp4")
        legacy = self.root / "legacy.json"
        legacy.write_text(json.dumps({"records": [{"id": "old", "project": "old", "status": "publishing",
                          "video": str(self.root / "private.mp4"), "claim_token": "obsolete"}]}))
        self.assertEqual(tasks.import_legacy(legacy)["imported"], 1)
        self.assertEqual(tasks.import_legacy(legacy)["imported"], 0)
        imported = tasks.list_tasks()[0]
        self.assertEqual(imported["status"], "needs_human")
        self.assertEqual(imported["video_url"], "")
        self.assertNotIn("claim_token", imported)

    def test_http_range_head_api_and_private_files(self):
        rec = self.create_ready()
        tasks.claim(rec["id"], "wechat-channels", "account")
        (self.root / "unistudio.local.json").write_text('{"secret":"do not expose"}')

        class QuietHandler(Handler):
            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        base = f"http://127.0.0.1:{server.server_port}"
        with urllib.request.urlopen(base + "/api/records") as response:
            body = response.read()
        self.assertNotIn(b"claim_token", body)
        self.assertEqual(json.loads(body)["records"][0]["status"], "publishing")
        video_url = base + rec["video_url"]
        for header, expected in (("bytes=0-9", self.movie.read_bytes()[:10]),
                                 ("bytes=-7", self.movie.read_bytes()[-7:])):
            with urllib.request.urlopen(urllib.request.Request(video_url, headers={"Range": header})) as response:
                self.assertEqual(response.status, 206)
                self.assertEqual(response.read(), expected)
        with urllib.request.urlopen(urllib.request.Request(video_url, method="HEAD")) as response:
            self.assertEqual(int(response.headers["Content-Length"]), self.movie.stat().st_size)
            self.assertEqual(response.read(), b"")
        for path in ("/unistudio.local.json", "/productions/state/tasks.db", "/.git/config",
                     "/projects/../../unistudio.local.json"):
            with self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(base + path)
            self.assertIn(error.exception.code, (403, 404))
        with self.assertRaises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(urllib.request.Request(video_url, headers={"Range": "bytes=999999999-"}))
        self.assertEqual(error.exception.code, 416)

    def test_preflight_missing_config_and_failed_tts_block_production(self):
        with patch.dict("os.environ", {"UNISTUDIO_CONFIG": str(self.root / "missing.json")}):
            report = check_environment()
            self.assertFalse(report["ok"])
            self.assertIn("config", [c["name"] for c in report["checks"] if not c["ok"]])
        cfg = {"hyperframes_command": ["hyperframes"], "tts": {"base_url": "http://127.0.0.1:1", "model": "demo", "voice": "demo"}}
        with patch("task_service.environment.load_config", return_value=cfg), patch("task_service.environment.subprocess.run") as run:
            run.return_value.stdout = "v22.0.0 hyperframes 0.8.158"
            report = check_environment()
        self.assertFalse(report["ok"])
        self.assertIn("tts_service", [c["name"] for c in report["checks"] if not c["ok"]])

    def test_cli_new_does_not_copy_when_preflight_fails(self):
        args = ["unistudio.py", "new", "--template", "demo", "--name", "blocked", "--brief", "demo"]
        with patch("sys.argv", args), patch("scripts.unistudio.check_environment", return_value={"ok": False}), \
                patch("scripts.unistudio.tasks.create") as create, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(unistudio.main(), 1)
            create.assert_not_called()
        self.assertFalse((self.projects / "blocked").exists())

    def test_tts_adapter_uses_configured_model_voice_and_measured_wav(self):
        audio = io.BytesIO()
        with wave.open(audio, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(24000)
            wav.writeframes(b"\0\0" * 2400)
        received = []

        class FakeTTS(Handler):
            def do_POST(self):
                received.append((json.loads(self.rfile.read(int(self.headers["Content-Length"]))),
                                 self.headers.get("Authorization")))
                self.send_response(200)
                self.send_header("Content-Type", "audio/wav")
                self.end_headers()
                self.wfile.write(audio.getvalue())

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), FakeTTS)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        text = self.root / "narration.txt"
        text.write_text("测试配音")
        cfg = {"tts": {"base_url": f"http://127.0.0.1:{server.server_port}", "model": "chosen-model",
                       "voice": "my-authorized-voice", "api_key_env": "TEST_TTS_SECRET"}}
        with patch("scripts.unistudio.load_config", return_value=cfg), patch.dict("os.environ", {"TEST_TTS_SECRET": "fixture-secret"}):
            result = unistudio.synthesize(text, self.projects / "demo/assets/audio/voice.wav")
        self.assertEqual(result["duration_s"], 0.1)
        self.assertEqual(received[0][0]["voice"], "my-authorized-voice")
        self.assertEqual(received[0][0]["model"], "chosen-model")
        self.assertEqual(received[0][1], "Bearer fixture-secret")
        self.assertNotIn("fixture-secret", json.dumps(result))


if __name__ == "__main__":
    unittest.main()
