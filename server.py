"""StreamLens local demo server with sandbox-only read streaming."""
from __future__ import annotations

import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

from stream_manager import StreamManager

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
API_KEY = os.environ.get("FP_API_KEY", "").strip()
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
manager = StreamManager(API_KEY, autostart_demo=False)


class Handler(BaseHTTPRequestHandler):
    server_version = "StreamLens/0.1"

    def log_message(self, format: str, *args) -> None:
        print("%s - %s" % (self.address_string(), format % args))

    def send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def serve_events(self) -> None:
        q = manager.subscribe()
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-store")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        try:
            while True:
                try:
                    message = q.get(timeout=12)
                except Exception:
                    self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
                    continue
                payload = json.dumps(message, separators=(",", ":"), ensure_ascii=False)
                self.wfile.write(f"data: {payload}\n\n".encode("utf-8"))
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass
        finally:
            manager.unsubscribe(q)

    def handle_api_get(self, path: str) -> None:
        if path == "/api/status":
            self.send_json(200, manager.status())
        elif path == "/api/events":
            self.serve_events()
        else:
            self.send_json(404, {"error": "Unknown local API route."})

    def do_GET(self) -> None:
        parsed = urlsplit(self.path)
        if parsed.path.startswith("/api/"):
            self.handle_api_get(parsed.path)
            return
        relative = unquote(parsed.path).lstrip("/") or "index.html"
        target = (STATIC / relative).resolve()
        if not target.is_relative_to(STATIC.resolve()) or not target.is_file():
            self.send_error(404, "Not found")
            return
        body = target.read_bytes()
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type in {"application/javascript", "application/json"}:
            content_type += "; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        client_host = self.client_address[0]
        try:
            from ipaddress import ip_address
            is_loopback = ip_address(client_host).is_loopback
        except ValueError:
            is_loopback = False
        origin = self.headers.get("Origin")
        if not is_loopback or (origin and urlsplit(origin).netloc not in {
            f"127.0.0.1:{PORT}", f"localhost:{PORT}", f"[::1]:{PORT}"
        }):
            self.send_json(403, {"error": "Local control routes accept same-origin loopback requests only."})
            return
        path = urlsplit(self.path).path
        try:
            if path == "/api/connect":
                self.send_json(200, {"ok": True, "status": manager.start_live()})
            elif path == "/api/disconnect":
                self.send_json(200, {"ok": True, "status": manager.disconnect()})
            elif path == "/api/demo":
                self.send_json(200, {"ok": True, "status": manager.start_demo()})
            elif path == "/api/demo-gap":
                self.send_json(200, {"ok": True, "status": manager.inject_demo_gap()})
            else:
                self.send_json(404, {"error": "Unknown local route. StreamLens has no trading-write routes."})
        except ValueError as error:
            self.send_json(400, {"error": str(error)})
        except RuntimeError as error:
            self.send_json(501, {"error": str(error)})


def main() -> None:
    if not STATIC.is_dir():
        raise SystemExit(f"Missing static app directory: {STATIC}")
    manager.start_demo()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"StreamLens running at http://{HOST}:{PORT} (sandbox-only observer; no order writes)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        manager.disconnect()
        server.server_close()


if __name__ == "__main__":
    main()
