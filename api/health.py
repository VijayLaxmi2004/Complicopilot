from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

ALLOWED_ORIGIN = "*"  # Adjust if you want to restrict


def _write_json(handler: BaseHTTPRequestHandler, status: int, payload: dict):
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
    handler.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "*")
    handler.end_headers()
    handler.wfile.write(body)


class handler(BaseHTTPRequestHandler):  # Vercel Python entrypoint must be named `handler`
    def do_OPTIONS(self):  # Preflight CORS
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_GET(self):
        payload = {
            "status": "ok",
            "service": "edge-api",
            "endpoint": "health",
            "version": "0.1.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        _write_json(self, 200, payload)
