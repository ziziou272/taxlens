"""Tests for Plaid account endpoints."""
import pytest


@pytest.mark.asyncio
async def test_link_returns_503_when_not_configured(client):
    resp = await client.post("/api/accounts/link")
    assert resp.status_code == 503
    assert "Plaid not configured" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_exchange_returns_503_when_not_configured(client):
    resp = await client.post("/api/accounts/exchange", json={"public_token": "test"})
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_list_accounts_empty(client):
    resp = await client.get("/api/accounts")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_holdings_returns_503_when_not_configured(client):
    resp = await client.get("/api/accounts/holdings")
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_sync_returns_503_when_not_configured(client):
    resp = await client.post("/api/accounts/sync")
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_disconnect_not_found(client):
    resp = await client.delete("/api/accounts/nonexistent")
    assert resp.status_code == 404
