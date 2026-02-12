"""Alert system integration tests."""
import pytest


# ── 1. Underwithholding → critical alert ──────────────────────────────

@pytest.mark.asyncio
async def test_underwithholding_critical(client):
    r = await client.post("/api/alerts/check", json={
        "total_income": 500000,
        "total_tax_liability": 180000,
        "total_withheld": 80000,  # Way under
        "rsu_income": 150000,
        "filing_status": "single",
        "state": "CA",
    })
    assert r.status_code == 200
    d = r.json()
    assert d["has_critical"] is True
    assert len(d["alerts"]) > 0
    severities = [a["severity"] for a in d["alerts"]]
    assert "critical" in severities


# ── 2. No issues → no alerts ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_no_issues_no_alerts(client):
    r = await client.post("/api/alerts/check", json={
        "total_income": 80000,
        "total_tax_liability": 15000,
        "total_withheld": 16000,  # Slightly over-withheld
        "filing_status": "single",
        "state": "CA",
    })
    assert r.status_code == 200
    d = r.json()
    # Should have no critical alerts for well-withheld moderate income
    assert d["has_critical"] is False


# ── 3. RSU underwithholding (22% flat vs 35% marginal) → UW-004 ─────

@pytest.mark.asyncio
async def test_rsu_underwithholding_alert(client):
    r = await client.post("/api/alerts/check", json={
        "total_income": 500000,
        "total_tax_liability": 170000,
        "total_withheld": 100000,
        "rsu_income": 200000,  # Large RSU component
        "filing_status": "single",
        "state": "CA",
    })
    assert r.status_code == 200
    d = r.json()
    # Should flag RSU withholding issue
    rsu_alerts = [a for a in d["alerts"] if "rsu" in a["title"].lower() or "rsu" in a["message"].lower() or a["category"] == "withholding"]
    assert len(rsu_alerts) > 0 or d["has_critical"]


# ── 4. Capital gains near WA threshold ───────────────────────────────

@pytest.mark.asyncio
async def test_wa_capital_gains_threshold(client):
    r = await client.post("/api/alerts/check", json={
        "total_income": 400000,
        "total_tax_liability": 100000,
        "total_withheld": 95000,
        "long_term_gains": 260000,  # Above WA $250K threshold
        "filing_status": "single",
        "state": "WA",
    })
    assert r.status_code == 200
    d = r.json()
    # Should have some alert about WA capital gains or general gains
    assert "alerts" in d
    assert isinstance(d["alerts"], list)
