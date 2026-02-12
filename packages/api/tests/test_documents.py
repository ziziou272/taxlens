"""Tests for document endpoints."""
import pytest
import io


@pytest.mark.asyncio
async def test_upload_document(client):
    file_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100  # minimal PNG-like bytes
    resp = await client.post(
        "/api/documents/upload",
        files={"file": ("w2-2024.png", io.BytesIO(file_content), "image/png")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "w2-2024.png"
    assert data["doc_type"] == "w2"
    assert data["status"] == "uploaded"


@pytest.mark.asyncio
async def test_upload_unsupported_type(client):
    resp = await client.post(
        "/api/documents/upload",
        files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_list_documents(client):
    resp = await client.get("/api/documents")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_get_document_not_found(client):
    resp = await client.get("/api/documents/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_document_not_found(client):
    resp = await client.delete("/api/documents/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_upload_and_get_document(client):
    file_content = b"\xff\xd8\xff\xe0" + b"\x00" * 100  # JPEG-like
    resp = await client.post(
        "/api/documents/upload",
        files={"file": ("1099-b-2024.jpg", io.BytesIO(file_content), "image/jpeg")},
    )
    assert resp.status_code == 200
    doc_id = resp.json()["id"]

    resp = await client.get(f"/api/documents/{doc_id}")
    assert resp.status_code == 200
    assert resp.json()["doc_type"] == "1099-b"


@pytest.mark.asyncio
async def test_confirm_document(client):
    file_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    resp = await client.post(
        "/api/documents/upload",
        files={"file": ("w2.png", io.BytesIO(file_content), "image/png")},
    )
    doc_id = resp.json()["id"]

    resp = await client.post(
        f"/api/documents/{doc_id}/confirm",
        json={"extracted_data": {"wages": 150000, "federal_tax": 30000}},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "confirmed"
    assert resp.json()["extracted_data"]["wages"] == 150000
