"""Tests for authentication and authorization."""
import pytest
from jose import jwt


class TestAnonymousMode:
    """When auth is not configured, everything works as before."""

    async def test_health_always_public(self, client):
        r = await client.get("/api/health")
        assert r.status_code == 200

    async def test_calculator_public(self, client):
        r = await client.post("/api/tax/calculate", json={
            "filing_status": "single", "wages": 100000, "state": "CA"
        })
        assert r.status_code == 200

    async def test_no_auth_config_allows_protected_routes(self, client, no_auth_settings):
        """Without JWT secret, protected routes still work (anonymous mode)."""
        r = await client.get("/api/users/me")
        assert r.status_code == 200


class TestAuthEnabled:
    """When auth is configured, protected routes require valid JWT."""

    async def test_protected_route_no_token_401(self, client, auth_settings):
        r = await client.get("/api/users/me")
        assert r.status_code == 401

    async def test_protected_route_invalid_token_401(self, client, auth_settings):
        r = await client.get("/api/users/me", headers={"Authorization": "Bearer bad-token"})
        assert r.status_code == 401

    async def test_protected_route_valid_token_200(self, client, auth_settings, auth_headers):
        r = await client.get("/api/users/me", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["supabase_user_id"] == "test-user-123"

    async def test_expired_token_401(self, client, auth_settings):
        token = jwt.encode(
            {"sub": "user1", "aud": "authenticated", "exp": 1},
            "test-jwt-secret-for-testing-only",
            algorithm="HS256",
        )
        r = await client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 401

    async def test_wrong_audience_401(self, client, auth_settings):
        token = jwt.encode(
            {"sub": "user1", "aud": "wrong", "exp": 9999999999},
            "test-jwt-secret-for-testing-only",
            algorithm="HS256",
        )
        r = await client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 401


class TestPublicEndpoints:
    """These should always be accessible regardless of auth config."""

    async def test_health(self, client, auth_settings):
        r = await client.get("/api/health")
        assert r.status_code == 200

    async def test_calculate(self, client, auth_settings):
        r = await client.post("/api/tax/calculate", json={
            "filing_status": "single", "wages": 100000, "state": "CA"
        })
        assert r.status_code == 200

    async def test_alert_check(self, client, auth_settings):
        r = await client.post("/api/alerts/check", json={
            "total_income": 200000,
            "total_tax_liability": 50000,
            "total_withheld": 30000,
            "filing_status": "single",
            "state": "CA",
        })
        assert r.status_code == 200

    async def test_scenario_types(self, client, auth_settings):
        r = await client.get("/api/scenarios/types")
        assert r.status_code == 200


class TestProtectedEndpoints:
    """These should return 401 without a token when auth is enabled."""

    async def test_documents_list_401(self, client, auth_settings):
        r = await client.get("/api/documents")
        assert r.status_code == 401

    async def test_accounts_list_401(self, client, auth_settings):
        r = await client.get("/api/accounts")
        assert r.status_code == 401

    async def test_scenario_save_401(self, client, auth_settings):
        r = await client.post("/api/scenarios/save", json={
            "name": "test", "parameters": {}
        })
        assert r.status_code == 401

    async def test_alerts_profile_401(self, client, auth_settings):
        r = await client.get("/api/alerts/some-profile-id")
        assert r.status_code == 401
