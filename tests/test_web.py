"""Offline deterministic transport and real Maru bridge tests; no public network."""
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("dlm74_web", ROOT / "adapters/web.py")
web = importlib.util.module_from_spec(spec)
spec.loader.exec_module(web)
BODY = '(error "NOT EXECUTABLE")\n외부 관찰'.encode()


class Handler(BaseHTTPRequestHandler):
    calls = 0

    def do_GET(self):
        type(self).calls += 1
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/doc")
            self.end_headers()
            return
        if self.path not in ("/doc", "/mirror", "/large"):
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"x" * 2048 if self.path == "/large" else BODY)

    def log_message(self, *args):
        pass


class WebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def client(self, **kwargs):
        return web.CachedWeb(self.tmp.name, **kwargs)

    def test_original_bytes_provenance_and_offline(self):
        url = self.base + "/redirect"
        record, error = self.client().get_record(url)
        self.assertIsNone(error)
        self.assertEqual(base64.b64decode(record["raw_base64"]), BODY)
        self.assertEqual(record["sha256"], hashlib.sha256(BODY).hexdigest())
        self.assertEqual(record["url"], url)
        self.assertEqual(record["final_url"], self.base + "/doc")
        calls = Handler.calls
        self.assertEqual(self.client(offline=True).get_record(url), (record, None))
        self.assertEqual(Handler.calls, calls)

    def test_bounded_failure_is_not_data(self):
        self.assertEqual(self.client(max_bytes=100).get_record(self.base + "/large")[1], "oversize-response")
        self.assertIsNone(self.client().get_record(self.base + "/missing")[0])
        self.assertEqual(self.client(offline=True).get_record(self.base + "/uncached")[1], "offline-miss")
        self.assertEqual(self.client().get_record("file:///etc/passwd")[1], "unsupported-url")

    def test_cache_hash_corruption_rejected(self):
        url = self.base + "/doc"
        record, _ = self.client().get_record(url)
        path = next((Path(self.tmp.name) / "fetch").glob("*.json"))
        record["sha256"] = "0" * 64
        path.write_text(json.dumps(record))
        self.assertEqual(self.client(offline=True).get_record(url)[1], "invalid-cache")

    def test_refresh_and_malformed_discovery(self):
        url = self.base + "/doc"
        first, _ = self.client().get_record(url)
        calls = Handler.calls
        refreshed, error = self.client(refresh=True).get_record(url)
        self.assertIsNone(error)
        self.assertGreater(Handler.calls, calls)
        self.assertEqual(first["sha256"], refreshed["sha256"])
        self.assertEqual(first["raw_base64"], refreshed["raw_base64"])
        class BrokenAPI:
            def get_json(self, url):
                return {"query": None, "items": None}
        for provider in ("github", "wikipedia"):
            self.assertEqual(web.search_urls(BrokenAPI(), "x", provider, 2), ([], "discovery-failed"))

    def test_external_text_cannot_become_code(self):
        record, _ = self.client().get_record(self.base + "/doc")
        form = web.document_form(record)
        self.assertTrue(form.isascii())
        self.assertNotIn("NOT EXECUTABLE", form)
        self.assertIn("(raw h" + BODY.hex() + ")", form)
        self.assertIn("(status acquired-uninterpreted)", form)

    def test_bridge_resume_deduplicate_and_failure(self):
        import os
        env = dict(os.environ, STORE=self.tmp.name)
        command = [str(ROOT / "scripts/web.sh"), "--url", self.base + "/doc", "--url", self.base + "/mirror", "--limit", "2"]
        first = subprocess.run(command, env=env, text=True, capture_output=True, timeout=30, check=True)
        self.assertIn("(documents 2)", first.stdout)
        self.assertIn("(content-groups 1)", first.stdout)
        self.assertIn("(admitted-facts 0)", first.stdout)
        second = subprocess.run(command + ["--offline"], env=env, text=True, capture_output=True, timeout=30, check=True)
        self.assertIn("(documents 2)", second.stdout)
        self.assertIn("(acquisitions 2)", second.stdout)
        third = subprocess.run([str(ROOT / "scripts/web.sh"), "--url", self.base + "/absent", "--offline"],
                               env=env, text=True, capture_output=True, timeout=30, check=True)
        self.assertIn('"fetched": 0', third.stdout)
        self.assertIn("(documents 2)", third.stdout)
        self.assertIn("(acquisitions 3)", third.stdout)
        self.assertIn("(interpretation unresolved)", third.stdout)
        refresh = subprocess.run(command + ["--refresh"], env=env, text=True, capture_output=True, timeout=30, check=True)
        self.assertIn("(documents 2)", refresh.stdout)
        self.assertIn("(acquisitions 4)", refresh.stdout)
        state_path = Path(self.tmp.name) / "state.sexp"
        saved = state_path.read_text()
        forged = saved.replace("(document d", "(document forged", 1)
        process = subprocess.run([str(ROOT / "scripts/run.sh"), "web-report"],
                                 input=forged, text=True, capture_output=True, timeout=30)
        self.assertNotEqual(process.returncode, 0)
        self.assertEqual(state_path.read_text(), saved)


if __name__ == "__main__":
    unittest.main()
