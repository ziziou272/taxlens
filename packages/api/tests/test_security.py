"""Tests for security features."""
import pytest


class TestSecurityHeaders:
    async def test_health_has_security_headers(self, client):
        r = await client.get("/api/health")
        assert r.headers.get("X-Content-Type-Options") == "nosniff"
        assert r.headers.get("X-Frame-Options") == "DENY"
        assert "Content-Security-Policy" in r.headers


class TestRateLimiting:
    """Rate limiting is configured via slowapi. Basic smoke test."""

    async def test_slowapi_registered(self):
        from app.main import app
        assert hasattr(app.state, "limiter")
