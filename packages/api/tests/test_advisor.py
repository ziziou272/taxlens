"""Tests for AI advisor endpoints."""
import pytest


@pytest.mark.asyncio
async def test_explain_returns_503_when_not_configured(client):
    resp = await client.post("/api/advisor/explain", json={"question": "What is AMT?"})
    assert resp.status_code == 503
    assert "not configured" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_recommend_returns_503_when_not_configured(client):
    resp = await client.post("/api/advisor/recommend", json={"tax_context": {"income": 300000}})
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_ask_returns_503_when_not_configured(client):
    resp = await client.post("/api/advisor/ask", json={"question": "Should I exercise my ISOs?"})
    assert resp.status_code == 503
