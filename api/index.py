"""Vercel Python Serverless Function entrypoint for /api/* routes.

Vercel automatically discovers `api/index.py` and invokes `handler` for each
HTTP request matched by vercel.json rewrites.
"""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

# Ensure repository root is importable inside Vercel's Python runtime.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.router import dispatch_request  # noqa: E402


class handler(BaseHTTPRequestHandler):  # noqa: N801 - Vercel requires lowercase `handler`
    """Vercel Serverless Function BaseHTTPRequestHandler implementation."""

    def _process(self, method: str) -> None:
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
        self._process("GET")

    def do_POST(self) -> None:  # noqa: N802
        self._process("POST")

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._process("OPTIONS")
