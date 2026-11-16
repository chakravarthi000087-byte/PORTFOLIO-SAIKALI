"""Standalone local Python HTTP server for development and Express proxying.

Run with:
    python3 -m backend.local_server --port 8001
"""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Tuple

from backend.router import dispatch_request


class PortfolioRequestHandler(BaseHTTPRequestHandler):
    """HTTP handler delegating /api/* traffic to backend.router.dispatch_request."""

    server_version = "PortfolioPythonBackend/1.0"

    def _handle(self, method: str) -> None:
        content_length = int(self.headers.get("Content-Length", "0") or "0")
        body_bytes = self.rfile.read(content_length) if content_length > 0 else b""
        status, headers, payload = dispatch_request(method, self.path, body_bytes)

        self.send_response(status)
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()

        if status != 204:
            self.wfile.write(json.dumps(payload).encode("utf-8"))

    def do_GET(self) -> None:  # noqa: N802
        self._handle("GET")

    def do_POST(self) -> None:  # noqa: N802
        self._handle("POST")

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._handle("OPTIONS")

    def log_message(self, format: str, *args: object) -> None:
        # Suppress noisy per-request stderr logs while keeping startup banner clean.
        return


def run_server(host: str = "127.0.0.1", port: int = 8001) -> Tuple[str, int]:
    """Start the blocking threaded HTTP server on host:port."""
    httpd = ThreadingHTTPServer((host, port), PortfolioRequestHandler)
    print(f"Python portfolio backend listening on http://{host}:{port}", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return host, port


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local Python backend for Sai's portfolio.")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind")
    parser.add_argument("--port", type=int, default=8001, help="TCP port to listen on")
    args = parser.parse_args()
    run_server(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
