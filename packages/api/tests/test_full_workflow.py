"""Full user workflow integration test.

Simulates a complete user session: calculate → alerts → scenario → document.
"""
import io
import pytest


@pytest.mark.asyncio
async def test_complete_user_workflow(client):
    """End-to-end: calculate tax → check alerts → run scenario → upload doc."""

    # Step 1: Calculate tax
    calc_r = await client.post("/api/tax/calculate", json={
        "filing_status": "single",
        "wages": 300000,
        "rsu_income": 150000,
        "capital_gains_long": 50000,
        "state": "CA",
    })
    assert calc_r.status_code == 200
    tax = calc_r.json()
    assert tax["total_income"] == 500000
    assert tax["total_tax"] > 0
    total_tax = tax["total_tax"]

    # Step 2: Check alerts using calculation results
    alert_r = await client.post("/api/alerts/check", json={
        "total_income": tax["total_income"],
        "total_tax_liability": tax["total_tax"],
        "total_withheld": 80000,  # Intentionally under-withheld
        "rsu_income": 150000,
        "long_term_gains": 50000,
        "filing_status": "single",
        "state": "CA",
    })
    assert alert_r.status_code == 200
    alerts = alert_r.json()
    assert "alerts" in alerts
    assert alerts["has_critical"] is True  # Under-withheld by a lot

    # Step 3: Run what-if scenario (what if I move to WA?)
    scenario_r = await client.post("/api/scenarios/run", json={
        "baseline": {
            "name": "Stay in CA",
            "wages": 300000,
            "rsu_income": 150000,
            "long_term_gains": 50000,
            "state": "CA",
        },
        "alternative": {
            "name": "Move to WA",
            "wages": 300000,
            "rsu_income": 150000,
            "long_term_gains": 50000,
            "state": "WA",
        },
    })
    assert scenario_r.status_code == 200
    scenario = scenario_r.json()
    assert scenario["tax_savings"] > 0
    assert scenario["baseline"]["total_tax"] > scenario["alternative"]["total_tax"]

    # Step 4: Upload a document
    pdf_bytes = b"%PDF-1.0\n1 0 obj<</Type/Catalog>>endobj\n%%EOF"
    doc_r = await client.post(
        "/api/documents/upload",
        files={"file": ("w2-2024.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    assert doc_r.status_code == 200
    doc = doc_r.json()
    assert doc["status"] == "uploaded"
    doc_id = doc["id"]

    # Step 5: Confirm document
    confirm_r = await client.post(f"/api/documents/{doc_id}/confirm", json={
        "extracted_data": {"wages": 300000, "federal_tax": 60000},
    })
    assert confirm_r.status_code == 200
    assert confirm_r.json()["status"] == "confirmed"

    # Step 6: Verify withholding gap
    gap_r = await client.post("/api/tax/withholding-gap", json={
        "filing_status": "single",
        "wages": 300000,
        "rsu_income": 150000,
        "capital_gains_long": 50000,
        "state": "CA",
        "ytd_federal_withheld": 60000,
        "ytd_state_withheld": 20000,
    })
    assert gap_r.status_code == 200
    gap = gap_r.json()
    assert gap["projected_total_tax"] > 0
    assert gap["gap"] > 0  # Under-withheld


@pytest.mark.asyncio
async def test_workflow_low_income_no_alerts(client):
    """Low income workflow — should have minimal/no alerts."""

    calc_r = await client.post("/api/tax/calculate", json={
        "filing_status": "single",
        "wages": 50000,
        "state": "CA",
    })
    assert calc_r.status_code == 200
    tax = calc_r.json()

    alert_r = await client.post("/api/alerts/check", json={
        "total_income": tax["total_income"],
        "total_tax_liability": tax["total_tax"],
        "total_withheld": tax["total_tax"] + 1000,  # Over-withheld
        "filing_status": "single",
        "state": "CA",
    })
    assert alert_r.status_code == 200
    assert alert_r.json()["has_critical"] is False
