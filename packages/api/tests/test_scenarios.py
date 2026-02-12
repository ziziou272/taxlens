"""Scenario endpoint tests."""
import pytest


@pytest.mark.asyncio
async def test_scenario_types(client):
    r = await client.get("/api/scenarios/types")
    assert r.status_code == 200
    types = r.json()
    assert len(types) >= 5
    assert any(t["type_id"] == "rsu_timing" for t in types)


@pytest.mark.asyncio
async def test_scenario_run(client):
    """Compare CA vs WA residency."""
    r = await client.post("/api/scenarios/run", json={
        "baseline": {
            "name": "Stay in CA",
            "wages": 300000,
            "rsu_income": 100000,
            "state": "CA",
        },
        "alternative": {
            "name": "Move to WA",
            "wages": 300000,
            "rsu_income": 100000,
            "state": "WA",
        },
    })
    assert r.status_code == 200
    data = r.json()
    assert data["tax_savings"] > 0  # WA should be cheaper (no state tax)
    assert data["baseline"]["total_tax"] > data["alternative"]["total_tax"]


@pytest.mark.asyncio
async def test_scenario_save(client):
    r = await client.post("/api/scenarios/save", json={
        "name": "Test scenario",
        "parameters": {"wages": 100000},
    })
    assert r.status_code == 200
    assert "id" in r.json()


@pytest.mark.asyncio
async def test_alert_check(client):
    r = await client.post("/api/alerts/check", json={
        "total_income": 500000,
        "total_tax_liability": 180000,
        "total_withheld": 100000,
        "long_term_gains": 50000,
        "rsu_income": 150000,
        "filing_status": "single",
        "state": "CA",
    })
    assert r.status_code == 200
    data = r.json()
    assert "summary" in data
    assert len(data["alerts"]) > 0  # Should have underwithholding alerts


@pytest.mark.asyncio
async def test_document_upload_requires_file(client):
    r = await client.post("/api/documents/upload")
    assert r.status_code == 422  # file field required
