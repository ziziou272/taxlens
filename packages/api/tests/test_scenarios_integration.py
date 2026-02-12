"""Scenario (what-if) integration tests."""
import pytest


# ── 1. RSU timing: sell this year vs next ─────────────────────────────

@pytest.mark.asyncio
async def test_rsu_timing_scenario(client):
    r = await client.post("/api/scenarios/run", json={
        "baseline": {
            "name": "Vest all RSU this year",
            "scenario_type": "rsu_timing",
            "wages": 300000,
            "rsu_income": 200000,
            "state": "CA",
        },
        "alternative": {
            "name": "Defer RSU to next year",
            "scenario_type": "rsu_timing",
            "wages": 300000,
            "rsu_income": 50000,
            "state": "CA",
        },
    })
    assert r.status_code == 200
    d = r.json()
    assert d["baseline"]["total_tax"] > d["alternative"]["total_tax"]
    assert d["tax_savings"] > 0
    assert d["savings_percentage"] > 0
    assert d["baseline"]["name"] == "Vest all RSU this year"
    assert d["alternative"]["name"] == "Defer RSU to next year"


# ── 2. State move: CA → WA ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_state_move_ca_to_wa(client):
    r = await client.post("/api/scenarios/run", json={
        "baseline": {
            "name": "Stay in CA",
            "scenario_type": "state_move",
            "wages": 400000,
            "rsu_income": 100000,
            "state": "CA",
        },
        "alternative": {
            "name": "Move to WA",
            "scenario_type": "state_move",
            "wages": 400000,
            "rsu_income": 100000,
            "state": "WA",
        },
    })
    assert r.status_code == 200
    d = r.json()
    assert d["tax_savings"] > 0  # WA has no income tax
    ca_tax = d["baseline"]["total_tax"]
    wa_tax = d["alternative"]["total_tax"]
    assert ca_tax > wa_tax
    # Savings should be significant (CA state tax on $500K is ~$30K+)
    assert d["tax_savings"] > 20000


# ── 3. Compare and identify best scenario ────────────────────────────

@pytest.mark.asyncio
async def test_compare_best_scenario(client):
    r = await client.post("/api/scenarios/run", json={
        "baseline": {
            "name": "High capital gains year",
            "wages": 200000,
            "long_term_gains": 300000,
            "state": "CA",
        },
        "alternative": {
            "name": "Defer gains",
            "wages": 200000,
            "long_term_gains": 50000,
            "state": "CA",
        },
    })
    assert r.status_code == 200
    d = r.json()
    # Alternative should be cheaper (less income)
    assert d["alternative"]["total_tax"] < d["baseline"]["total_tax"]
    assert d["tax_savings"] > 0
    # Best scenario is alternative (lower tax)
    best = d["alternative"] if d["alternative"]["total_tax"] < d["baseline"]["total_tax"] else d["baseline"]
    assert best["name"] == "Defer gains"


# ── 4. Save and retrieve scenario ────────────────────────────────────

@pytest.mark.asyncio
async def test_save_and_list_scenario(client):
    r = await client.post("/api/scenarios/save", json={
        "name": "Integration test scenario",
        "scenario_type": "custom",
        "parameters": {"wages": 250000, "state": "CA"},
        "total_tax": 75000,
    })
    assert r.status_code == 200
    d = r.json()
    assert "id" in d
    assert d["name"] == "Integration test scenario"
    assert d["message"] == "Scenario saved"

    # Verify scenario types are available
    r2 = await client.get("/api/scenarios/types")
    assert r2.status_code == 200
    types = r2.json()
    type_ids = [t["type_id"] for t in types]
    assert "rsu_timing" in type_ids
    assert "state_move" in type_ids
    assert "custom" in type_ids
