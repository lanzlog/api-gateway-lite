"""Middleware components for the API Gateway."""
import time


class AuthMiddleware:
    """API key authentication middleware."""

    def __init__(self):
        self._api_keys: dict[str, dict] = {}

    def register_key(self, key: str, owner: str, scopes: list[str] = None):
        self._api_keys[key] = {"owner": owner, "scopes": scopes or ["read"]}

    def validate(self, api_key: str) -> dict | None:
        return self._api_keys.get(api_key)


class CORSMiddleware:
    """CORS headers middleware."""

    DEFAULT_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]

    @classmethod
    def get_headers(cls, origin: str = "*") -> dict[str, str]:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": ", ".join(cls.DEFAULT_METHODS),
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }


class CacheMiddleware:
    """Simple in-memory response cache."""

    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self._cache: dict[str, tuple[float, any]] = {}

    def get(self, key: str):
        if key in self._cache:
            ts, val = self._cache[key]
            if time.time() - ts < self.ttl:
                return val
            del self._cache[key]
        return None

    def set(self, key: str, value):
        self._cache[key] = (time.time(), value)
