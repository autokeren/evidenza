"""Demo checkout app — the test target for evidenza verification.

This is a simple HTTP server that simulates a checkout API. The evidenza
agent writes code like this, runs tests against it, and records the evidence.

TODO(M3): expand with edge cases (invalid card, timeout handling).
"""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer


def process_checkout(payload: dict) -> tuple[int, dict]:
    """Process a checkout request. Returns (status_code, response_body).

    A minimal implementation for demo purposes.
    """
    if not payload.get("items"):
        return 400, {"error": "items required"}

    if not payload.get("card"):
        return 400, {"error": "card required"}

    total = sum(item.get("price", 0) * item.get("qty", 1) for item in payload["items"])
    return 200, {"status": "ok", "total": total, "items": len(payload["items"])}


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        code, resp = process_checkout(body)
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(resp).encode())

    def log_message(self, *args) -> None:
        pass  # quiet


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8080), Handler)
    print("Demo checkout API on http://127.0.0.1:8080")
    server.serve_forever()
