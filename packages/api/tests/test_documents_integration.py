"""Document upload and management integration tests."""
import io
import pytest


# ── 1. Upload a PDF → verify accepted ────────────────────────────────

@pytest.mark.asyncio
async def test_upload_pdf(client):
    pdf_bytes = b"%PDF-1.0\n1 0 obj<</Type/Catalog>>endobj\n%%EOF"
    r = await client.post(
        "/api/documents/upload",
        files={"file": ("w2-2024.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    assert r.status_code == 200
    d = r.json()
    assert d["filename"] == "w2-2024.pdf"
    assert d["status"] == "uploaded"
    assert "id" in d


# ── 2. List documents → verify returned ──────────────────────────────

@pytest.mark.asyncio
async def test_list_documents_after_upload(client):
    # Upload one first
    pdf_bytes = b"%PDF-1.0\n%%EOF"
    await client.post(
        "/api/documents/upload",
        files={"file": ("1099-2024.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    r = await client.get("/api/documents")
    assert r.status_code == 200
    docs = r.json()
    assert isinstance(docs, list)
    assert len(docs) >= 1


# ── 3. Get document detail ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_document_detail(client):
    pdf_bytes = b"%PDF-1.0\n%%EOF"
    r = await client.post(
        "/api/documents/upload",
        files={"file": ("w2-test.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    doc_id = r.json()["id"]

    r2 = await client.get(f"/api/documents/{doc_id}")
    assert r2.status_code == 200
    d = r2.json()
    assert d["id"] == doc_id
    assert d["filename"] == "w2-test.pdf"


# ── 4. Confirm document data ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_confirm_document_data(client):
    pdf_bytes = b"%PDF-1.0\n%%EOF"
    r = await client.post(
        "/api/documents/upload",
        files={"file": ("w2-confirm.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    doc_id = r.json()["id"]

    r2 = await client.post(f"/api/documents/{doc_id}/confirm", json={
        "extracted_data": {
            "wages": 200000,
            "federal_tax_withheld": 45000,
            "state_tax_withheld": 15000,
            "employer": "TechCo Inc",
        },
    })
    assert r2.status_code == 200
    d = r2.json()
    assert d["status"] == "confirmed"
    assert d["extracted_data"]["wages"] == 200000
    assert d["extracted_data"]["employer"] == "TechCo Inc"
