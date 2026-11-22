from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

PORT = int(os.environ.get("PORT", 3000))
SECONDARY_PORT = int(os.environ.get("SECONDARY_PORT", 5000))
SERVE_DIR = os.environ.get("SERVE_DIR", ".")
API_TARGET = os.environ.get("API_TARGET", "http://127.0.0.1:8000").rstrip("/")

ROUTES = {
    "/": "/index.html",
    "": "/index.html",
    "/index.html": "/index.html",
    "/gifts": "/index.html",
    "/samurai": "/samurai.html",
    "/samurai.html": "/samurai.html",
    "/fmstar": "/fmstar_studio.html",
    "/fmstar_studio": "/fmstar_studio.html",
    "/fmstar_studio.html": "/fmstar_studio.html",
    "/jm-studio": "/jm_studio.html",
    "/jm_studio": "/jm_studio.html",
    "/studio": "/jm_studio.html",
}

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "host",
}


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class FMStarHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SERVE_DIR, **kwargs)

    def _is_api_request(self) -> bool:
        path = urlparse(self.path).path
        return path == "/api" or path.startswith("/api/")

    def _proxy_api(self):
        target_url = f"{API_TARGET}{self.path}"
        content_length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(content_length) if content_length > 0 else None

        headers = {
            k: v
            for k, v in self.headers.items()
            if k.lower() not in HOP_BY_HOP_HEADERS and k.lower() != "content-length"
        }
        if body is not None:
            headers["Content-Length"] = str(len(body))

        req = Request(target_url, data=body, headers=headers, method=self.command)

        try:
            with urlopen(req, timeout=30) as resp:
                resp_body = resp.read()
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() not in HOP_BY_HOP_HEADERS:
                        self.send_header(k, v)
                self.end_headers()
                if resp_body:
                    self.wfile.write(resp_body)
        except HTTPError as e:
            err_body = e.read() if e.fp else b""
            self.send_response(e.code)
            for k, v in e.headers.items():
                if k.lower() not in HOP_BY_HOP_HEADERS:
                    self.send_header(k, v)
            self.end_headers()
            if err_body:
                self.wfile.write(err_body)
        except URLError as e:
            self.send_response(502)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            payload = f'{{"error": "API backend unreachable", "detail": "{str(e.reason)}"}}'
            self.wfile.write(payload.encode("utf-8"))

    def do_GET(self):
        try:
            if self._is_api_request():
                return self._proxy_api()

            parsed = urlparse(self.path)
            clean_path = parsed.path if parsed.path == "/" else parsed.path.rstrip("/")

            if clean_path in ROUTES:
                target = ROUTES[clean_path]
                self.path = f"{target}?{parsed.query}" if parsed.query else target

            return super().do_GET()
        except (ConnectionResetError, BrokenPipeError):
            pass
        except Exception as e:
            try:
                self.send_error(500, str(e))
            except Exception:
                pass

    def _handle_body_method(self):
        try:
            if self._is_api_request():
                return self._proxy_api()
            self.send_error(405, "Method Not Allowed")
        except (ConnectionResetError, BrokenPipeError):
            pass

    def do_POST(self):
        self._handle_body_method()

    def do_PUT(self):
        self._handle_body_method()

    def do_PATCH(self):
        self._handle_body_method()

    def do_DELETE(self):
        self._handle_body_method()

    def do_OPTIONS(self):
        if self._is_api_request():
            return self._proxy_api()
        self.send_response(204)
        self.end_headers()

    def log_message(self, format, *args):
        if args and str(args[1]).startswith(("4", "5")):
            super().log_message(format, *args)


def ensure_directories():
    for folder in (
        "outputs",
        "static/outputs",
        "fmstar-project/static/outputs",
        "public",
    ):
        os.makedirs(folder, exist_ok=True)


def run_secondary_port():
    try:
        print(f"⚔️ الساموراي جاهز! الخادم يعمل على http://127.0.0.1:{SECONDARY_PORT}")
        with ReusableThreadingHTTPServer(("", SECONDARY_PORT), FMStarHandler) as server:
            server.serve_forever()
    except Exception as e:
        print(f"Secondary port ({SECONDARY_PORT}) notice: {e}")


if __name__ == "__main__":
    ensure_directories()

    if SECONDARY_PORT != PORT:
        threading.Thread(target=run_secondary_port, daemon=True).start()

    print(f"🚀 Running FMStar & Studio Server on http://0.0.0.0:{PORT} (API -> {API_TARGET}) ...")
    while True:
        try:
            with ReusableThreadingHTTPServer(("", PORT), FMStarHandler) as server:
                server.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 تم إيقاف الخادم.")
            break
        except Exception as e:
            print(f"⚠️ إعادة محاولة تشغيل المنفذ {PORT} بعد خطأ: {e}")
            time.sleep(1)
