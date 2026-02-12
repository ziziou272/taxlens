"""Tests for user CRUD endpoints."""
import pytest


class TestUserCRUD:
    async def test_get_me_creates_user(self, client, auth_settings, auth_headers):
        r = await client.get("/api/users/me", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["supabase_user_id"] == "test-user-123"
        assert data["id"]  # auto-generated UUID

    async def test_update_me(self, client, auth_settings, auth_headers):
        # Create user first
        await client.get("/api/users/me", headers=auth_headers)
        # Update
        r = await client.patch("/api/users/me", headers=auth_headers, json={
            "name": "Test User", "email": "test@example.com"
        })
        assert r.status_code == 200
        assert r.json()["name"] == "Test User"
        assert r.json()["email"] == "test@example.com"

    async def test_delete_me(self, client, auth_settings, auth_headers):
        # Create user first
        await client.get("/api/users/me", headers=auth_headers)
        # Delete
        r = await client.delete("/api/users/me", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["status"] == "deleted"

    async def test_get_sessions(self, client, auth_settings, auth_headers):
        r = await client.get("/api/users/me/sessions", headers=auth_headers)
        assert r.status_code == 200

    async def test_get_audit_log(self, client, auth_settings, auth_headers):
        # Create user, then update to generate audit log
        await client.get("/api/users/me", headers=auth_headers)
        await client.patch("/api/users/me", headers=auth_headers, json={"name": "X"})
        r = await client.get("/api/users/me/audit-log", headers=auth_headers)
        assert r.status_code == 200
        logs = r.json()
        assert len(logs) >= 1
        assert logs[0]["action"] == "profile_update"


class TestDataIsolation:
    """User A should not see User B's data."""

    async def test_users_isolated(self, client, auth_settings, auth_headers, auth_headers_b):
        # Create both users
        r_a = await client.get("/api/users/me", headers=auth_headers)
        r_b = await client.get("/api/users/me", headers=auth_headers_b)
        assert r_a.json()["supabase_user_id"] != r_b.json()["supabase_user_id"]

        # Update user A
        await client.patch("/api/users/me", headers=auth_headers, json={"name": "Alice"})
        # User B should not have Alice's name
        r_b2 = await client.get("/api/users/me", headers=auth_headers_b)
        assert r_b2.json()["name"] != "Alice"

    async def test_documents_isolated(self, client, auth_settings, auth_headers, auth_headers_b):
        # List docs for both users — should be independent empty lists
        r_a = await client.get("/api/documents", headers=auth_headers)
        r_b = await client.get("/api/documents", headers=auth_headers_b)
        assert r_a.status_code == 200
        assert r_b.status_code == 200
        assert r_a.json() == []
        assert r_b.json() == []
