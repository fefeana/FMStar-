import http.client
import json
import os
import socket
import subprocess
import sys
import time
import unittest


def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class FMStarStudioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = _get_free_port()
        env = os.environ.copy()
        env["PORT"] = str(cls.port)
        env.pop("OMNIROUTE_BASE_URL", None)
        env.pop("OMNIROUTE_CLOUD_URL", None)
        env.pop("OMNIROUTE_API_KEY", None)
        env.pop("GEMINI_API_KEY", None)
        cls.proc = subprocess.Popen(
            [sys.executable, "server_3000.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        deadline = time.time() + 8.0
        while time.time() < deadline:
            if cls.proc.poll() is not None:
                raise RuntimeError("server_3000.py exited unexpectedly during test startup")
            try:
                conn = http.client.HTTPConnection("127.0.0.1", cls.port, timeout=1)
                conn.request("GET", "/api/v1/health")
                resp = conn.getresponse()
                resp.read()
                conn.close()
                if resp.status == 200:
                    return
            except Exception:
                time.sleep(0.15)
        raise TimeoutError("Timed out waiting for server_3000.py to listen")

    @classmethod
    def tearDownClass(cls):
        if cls.proc:
            if cls.proc.poll() is None:
                cls.proc.terminate()
                try:
                    cls.proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    cls.proc.kill()
                    cls.proc.wait(timeout=5)
            if cls.proc.stdout:
                cls.proc.stdout.close()
            if cls.proc.stderr:
                cls.proc.stderr.close()

    def test_health_endpoint(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request("GET", "/api/v1/health", headers={"Origin": "https://fefeana.github.io"})
        resp = conn.getresponse()
        data = json.loads(resp.read().decode("utf-8"))
        allow_origin = resp.getheader("Access-Control-Allow-Origin")
        conn.close()
        self.assertEqual(resp.status, 200)
        self.assertEqual(data.get("status"), "ok")
        self.assertFalse(data.get("omniroute_configured"))
        self.assertEqual(allow_origin, "https://fefeana.github.io")

    def test_cors_options_for_github_pages(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request(
            "OPTIONS",
            "/api/v1/studio/generate",
            headers={
                "Origin": "https://fefeana.github.io",
                "Access-Control-Request-Method": "POST",
            },
        )
        resp = conn.getresponse()
        resp.read()
        allow_origin = resp.getheader("Access-Control-Allow-Origin")
        conn.close()
        self.assertIn(resp.status, (200, 204))
        self.assertEqual(allow_origin, "https://fefeana.github.io")

    def test_v1_generate_empty_prompt_returns_400(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request(
            "POST",
            "/api/v1/studio/generate",
            body=json.dumps({"prompt": "   "}),
            headers={"Content-Type": "application/json", "Origin": "https://fefeana.github.io"},
        )
        resp = conn.getresponse()
        data = json.loads(resp.read().decode("utf-8"))
        conn.close()
        self.assertEqual(resp.status, 400)
        self.assertFalse(data.get("ok"))

    def test_v1_generate_and_tasks(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        body = json.dumps({"prompt": "قصيدة قصيرة عن الفجر"})
        conn.request(
            "POST",
            "/api/v1/studio/generate",
            body=body,
            headers={"Content-Type": "application/json", "Origin": "https://fefeana.github.io"},
        )
        resp = conn.getresponse()
        data = json.loads(resp.read().decode("utf-8"))
        conn.close()
        self.assertEqual(resp.status, 200)
        self.assertTrue(data.get("ok"))
        self.assertIn("task_id", data)

        conn2 = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn2.request(
            "POST",
            "/api/v1/tasks",
            body=json.dumps({"task_id": data["task_id"]}),
            headers={"Content-Type": "application/json"},
        )
        resp2 = conn2.getresponse()
        task_data = json.loads(resp2.read().decode("utf-8"))
        conn2.close()
        self.assertEqual(resp2.status, 200)
        self.assertTrue(task_data.get("ok"))
        self.assertEqual(task_data["task"]["id"], data["task_id"])

    def test_index_has_studio_engine_and_preview_helper(self):
        with open("index.html", "r", encoding="utf-8") as f:
            html = f.read()
        self.assertIn("fmstarStudioEngine", html)
        self.assertIn("fmstarGenerateAndPreview", html)
        self.assertIn("/api/v1/studio/generate", html)


if __name__ == "__main__":
    unittest.main()
