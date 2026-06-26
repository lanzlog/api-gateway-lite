"""Tests for the API Gateway."""
import unittest
from src.gateway import RateLimiter
from src.middleware import AuthMiddleware, CacheMiddleware


class TestRateLimiter(unittest.TestCase):
    def test_allows_under_limit(self):
        rl = RateLimiter(max_requests=5, window_seconds=60)
        for _ in range(5):
            self.assertTrue(rl.is_allowed("client1"))

    def test_blocks_over_limit(self):
        rl = RateLimiter(max_requests=2, window_seconds=60)
        self.assertTrue(rl.is_allowed("client1"))
        self.assertTrue(rl.is_allowed("client1"))
        self.assertFalse(rl.is_allowed("client1"))

    def test_separate_clients(self):
        rl = RateLimiter(max_requests=1, window_seconds=60)
        self.assertTrue(rl.is_allowed("client1"))
        self.assertTrue(rl.is_allowed("client2"))


class TestAuthMiddleware(unittest.TestCase):
    def test_register_and_validate(self):
        auth = AuthMiddleware()
        auth.register_key("key123", "user1", ["read", "write"])
        result = auth.validate("key123")
        self.assertIsNotNone(result)
        self.assertEqual(result["owner"], "user1")

    def test_invalid_key(self):
        auth = AuthMiddleware()
        self.assertIsNone(auth.validate("invalid"))


class TestCacheMiddleware(unittest.TestCase):
    def test_set_and_get(self):
        cache = CacheMiddleware(ttl_seconds=300)
        cache.set("key1", {"data": "test"})
        self.assertEqual(cache.get("key1"), {"data": "test"})

    def test_miss(self):
        cache = CacheMiddleware()
        self.assertIsNone(cache.get("nonexistent"))


if __name__ == "__main__":
    unittest.main()
