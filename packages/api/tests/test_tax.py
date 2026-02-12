"""Tax calculation endpoint tests."""
import pytest


@pytest.mark.asyncio
async def test_simple_w2(client):
    """Simple W-2 wages only."""
    r = await client.post("/api/tax/calculate", json={
        "filing_status": "single",
        "wages": 100000,
        "state": "CA",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["total_tax"] > 0
    assert data["federal_tax"] > 0
    assert data["state_tax"] > 0
    assert data["effective_rate"] > 0


@pytest.mark.asyncio
async def test_high_income_rsu(client):
    """High income with RSU."""
    r = await client.post("/api/tax/calculate", json={
        "filing_status": "single",
        "wages": 300000,
        "rsu_income": 150000,
        "capital_gains_long": 50000,
        "state": "CA",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["total_income"] == 500000
    assert data["total_tax"] > 100000  # High income = high tax
    assert data["niit"] > 0  # NIIT should apply


@pytest.mark.asyncio
async def test_married_filing(client):
    """Married filing jointly."""
    r = await client.post("/api/tax/calculate", json={
        "filing_status": "married_jointly",
        "wages": 200000,
        "state": "CA",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["filing_status"] == "married_jointly"
    assert data["deduction_used"] > 20000  # Married deduction is higher


@pytest.mark.asyncio
async def test_no_state_tax(client):
    """Washington state — no income tax."""
    r = await client.post("/api/tax/calculate", json={
        "filing_status": "single",
        "wages": 150000,
        "state": "WA",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["state_tax"] == 0


@pytest.mark.asyncio
async def test_withholding_gap(client):
    r = await client.post("/api/tax/withholding-gap", json={
        "filing_status": "single",
        "wages": 300000,
        "rsu_income": 100000,
        "state": "CA",
        "ytd_federal_withheld": 50000,
        "ytd_state_withheld": 10000,
    })
    assert r.status_code == 200
    data = r.json()
    assert "gap" in data
    assert data["projected_total_tax"] > 0
