"""API Gateway - Main entry point."""
import json
import http.server
import urllib.parse
from datetime import datetime


class RateLimiter:
    """Simple in-memory rate limiter using token bucket algorithm."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self._buckets: dict[str, list[float]] = {}

    def is_allowed(self, client_id: str) -> bool:
        now = datetime.now().timestamp()
        if client_id not in self._buckets:
            self._buckets[client_id] = []
        self._buckets[client_id] = [
            t for t in self._buckets[client_id] if now - t < self.window
        ]
        if len(self._buckets[client_id]) >= self.max_requests:
            return False
        self._buckets[client_id].append(now)
        return True


class RequestLogger:
    """Logs incoming requests with timestamp and metadata."""

    @staticmethod
    def log(method: str, path: str, status: int, client: str):
        ts = datetime.now().isoformat()
        print(f"[{ts}] {method} {path} -> {status} | client={client}")


class GatewayHandler(http.server.BaseHTTPRequestHandler):
    """Main gateway request handler."""

    rate_limiter = RateLimiter()
    logger = RequestLogger()

    def do_GET(self):
        client_ip = self.client_address[0]
        if not self.rate_limiter.is_allowed(client_ip):
            self._respond(429, {"error": "Rate limit exceeded"})
            return
        parsed = urllib.parse.urlparse(self.path)
        self._respond(200, {
            "status": "ok",
            "path": parsed.path,
            "timestamp": datetime.now().isoformat(),
        })

    def _respond(self, code: int, body: dict):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body, indent=2).encode())
        self.logger.log(self.command, self.path, code, self.client_address[0])


def main():
    port = 8080
    server = http.server.HTTPServer(("0.0.0.0", port), GatewayHandler)
    print(f"API Gateway running on http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
