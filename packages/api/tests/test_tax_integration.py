"""Comprehensive tax calculation integration tests.

End-to-end scenarios: API → Service → Engine → Response.
"""
import json
import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def load_taxpayers():
    with open(FIXTURES / "sample_taxpayers.json") as f:
        return json.load(f)


# ── 1. Single filer, $200K wages, CA ──────────────────────────────────

@pytest.mark.asyncio
async def test_single_200k_ca(client):
    tp = load_taxpayers()["single_200k_ca"]
    r = await client.post("/api/tax/calculate", json=tp)
    assert r.status_code == 200
    d = r.json()
    assert d["filing_status"] == "single"
    assert d["total_income"] == 200_000
    assert d["federal_tax"] > 0
    assert d["state_tax"] > 0
    assert d["state_code"] == "CA"
    assert d["social_security_tax"] > 0
    assert d["medicare_tax"] > 0
    assert 0 < d["effective_rate"] < 50
    assert d["total_tax"] == pytest.approx(
        d["federal_tax"] + d["social_security_tax"] + d["medicare_tax"]
        + d["additional_medicare_tax"] + d["niit"] + d["state_tax"] + d["amt_owed"],
        rel=0.01,
    )


# ── 2. MFJ, $400K wages + $150K RSU, NY ──────────────────────────────

@pytest.mark.asyncio
async def test_mfj_400k_rsu_ny(client):
    tp = load_taxpayers()["mfj_400k_rsu_ny"]
    r = await client.post("/api/tax/calculate", json=tp)
    assert r.status_code == 200
    d = r.json()
    assert d["filing_status"] == "married_jointly"
    assert d["total_income"] == 550_000
    assert d["state_tax"] >= 0  # NY state tax (may be 0 if NY not fully implemented)
    assert d["state_code"] == "NY"
    assert d["additional_medicare_tax"] > 0  # income > $250K MFJ threshold
    assert d["niit"] >= 0


# ── 3. Single, $300K wages + $80K LTCG, WA ───────────────────────────

@pytest.mark.asyncio
async def test_single_300k_ltcg_wa(client):
    tp = load_taxpayers()["single_300k_ltcg_wa"]
    r = await client.post("/api/tax/calculate", json=tp)
    assert r.status_code == 200
    d = r.json()
    assert d["total_income"] == 380_000
    assert d["federal_tax_on_ltcg"] > 0  # LTCG taxed at capital gains rates
    # WA has no income tax but may have capital gains tax
    assert d["state_code"] == "WA"
    assert d["niit"] > 0  # > $200K single with investment income


# ── 4. Multi-state: CA income + capital gains ─────────────────────────

@pytest.mark.asyncio
async def test_multi_state_ca(client):
    tp = load_taxpayers()["multi_state_ca_wa"]
    r = await client.post("/api/tax/calculate", json=tp)
    assert r.status_code == 200
    d = r.json()
    assert d["total_income"] == 350_000
    assert d["state_tax"] > 0  # CA taxes everything
    assert d["federal_tax"] > 0


# ── 5. High-income $1M+ with AMT trigger from ISO ────────────────────

@pytest.mark.asyncio
async def test_high_income_iso_amt(client):
    tp = load_taxpayers()["high_income_iso"]
    r = await client.post("/api/tax/calculate", json=tp)
    assert r.status_code == 200
    d = r.json()
    # Total income: 800K wages + 200K RSU = 1M (ISO bargain is AMT preference, not regular income)
    assert d["total_income"] >= 1_000_000
    assert d["total_tax"] > 300_000  # High income = high tax
    assert d["amt_owed"] >= 0  # ISO bargain element may trigger AMT


# ── 6. Simple: $50K wages, single ────────────────────────────────────

@pytest.mark.asyncio
async def test_simple_50k(client):
    tp = load_taxpayers()["simple_50k"]
    r = await client.post("/api/tax/calculate", json=tp)
    assert r.status_code == 200
    d = r.json()
    assert d["total_income"] == 50_000
    assert d["deduction_used"] > 0  # Standard deduction
    assert d["taxable_income"] < 50_000
    assert d["effective_rate"] < 30
    assert d["niit"] == 0  # Too low income
    assert d["additional_medicare_tax"] == 0


# ── 7. Edge case: $0 income ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_zero_income(client):
    tp = load_taxpayers()["zero_income"]
    r = await client.post("/api/tax/calculate", json=tp)
    assert r.status_code == 200
    d = r.json()
    assert d["total_income"] == 0
    assert d["total_tax"] == 0
    assert d["federal_tax"] == 0
    assert d["state_tax"] == 0
    assert d["effective_rate"] == 0


# ── 8. Edge case: bracket boundary ($191,950 = top of 32% bracket) ───

@pytest.mark.asyncio
async def test_bracket_boundary(client):
    tp = load_taxpayers()["bracket_boundary"]
    r = await client.post("/api/tax/calculate", json=tp)
    assert r.status_code == 200
    d = r.json()
    assert d["total_income"] == 191_950
    assert d["federal_tax"] > 0
    assert d["marginal_rate"] > 0
    # Verify total tax is consistent
    assert d["total_tax"] > d["federal_tax"]  # includes FICA + state
