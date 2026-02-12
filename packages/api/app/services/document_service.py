"""Document OCR service using Claude Vision API."""
from __future__ import annotations

import json
import os
import uuid

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.document import Document

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/jpg": "jpg",
}

EXTRACTION_PROMPTS = {
    "w2": "Extract from this W-2: employer name, wages (Box 1), federal tax withheld (Box 2), Social Security wages (Box 3), Social Security tax (Box 4), Medicare wages (Box 5), Medicare tax (Box 6), state wages (Box 16), state tax withheld (Box 17), and all Box 12 codes/amounts. Return JSON.",
    "1099-b": "Extract from this 1099-B: description of property, date acquired, date sold, proceeds (1d), cost basis (1e), gain/loss, short-term or long-term, and wash sale loss disallowed if any. Return JSON array of transactions.",
    "1099-div": "Extract from this 1099-DIV: total ordinary dividends (1a), qualified dividends (1b), total capital gain distributions (2a), unrecaptured Section 1250 gain (2b), Section 199A dividends (5), foreign tax paid (7). Return JSON.",
    "3922": "Extract from this Form 3922 (ESPP): date option granted, date option exercised, FMV per share on grant date, FMV per share on exercise date, exercise price per share, number of shares transferred. Return JSON.",
}

SYSTEM_PROMPT = """You are a tax document data extraction expert. Extract the requested fields accurately from the document image. Return ONLY valid JSON with the extracted data. If a field is not visible or not applicable, use null."""


def _detect_doc_type(filename: str) -> str:
    """Guess document type from filename."""
    lower = filename.lower()
    if "w2" in lower or "w-2" in lower:
        return "w2"
    if "1099-b" in lower or "1099b" in lower:
        return "1099-b"
    if "1099-div" in lower or "1099div" in lower:
        return "1099-div"
    if "3922" in lower:
        return "3922"
    return "unknown"


async def upload_document(file: UploadFile, user_id: str, db: AsyncSession) -> dict:
    """Upload a document and optionally extract data via Claude Vision."""
    content_type = file.content_type or ""
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {content_type}")

    # Save file
    os.makedirs(settings.upload_dir, exist_ok=True)
    file_id = str(uuid.uuid4())
    ext = ALLOWED_TYPES[content_type]
    filename = f"{file_id}.{ext}"
    file_path = os.path.join(settings.upload_dir, filename)

    data = await file.read()
    with open(file_path, "wb") as f:
        f.write(data)

    doc_type = _detect_doc_type(file.filename or "")

    doc = Document(
        id=file_id,
        user_id=user_id,
        filename=file.filename or filename,
        file_path=file_path,
        doc_type=doc_type,
        status="uploaded",
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # Try extraction if API key is configured and it's an image
    if settings.anthropic_api_key and doc_type != "unknown" and ext in ("jpg", "png"):
        try:
            extracted = await _extract_with_claude(file_path, doc_type, ext)
            doc.extracted_data = json.dumps(extracted)
            doc.status = "extracted"
            await db.commit()
        except Exception:
            doc.status = "extraction_failed"
            await db.commit()

    return _doc_to_dict(doc)


async def _extract_with_claude(file_path: str, doc_type: str, ext: str) -> dict:
    """Extract data from document image using Claude Vision."""
    import anthropic
    import base64

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    with open(file_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    media_type = "image/jpeg" if ext == "jpg" else f"image/{ext}"
    prompt = EXTRACTION_PROMPTS.get(doc_type, "Extract all relevant tax data from this document. Return JSON.")

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_data}},
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )

    # Parse JSON from response
    text = message.content[0].text
    # Try to extract JSON from the response
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON in the text
        import re
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"raw_text": text}


async def list_documents(user_id: str, db: AsyncSession) -> list[dict]:
    """List all documents for a user."""
    result = await db.execute(
        select(Document).where(Document.user_id == user_id).order_by(Document.created_at.desc())
    )
    return [_doc_to_dict(doc) for doc in result.scalars().all()]


async def get_document(doc_id: str, user_id: str, db: AsyncSession) -> dict:
    """Get a single document with extracted data."""
    result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.user_id == user_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return _doc_to_dict(doc)


async def confirm_document(doc_id: str, user_id: str, extracted_data: dict, db: AsyncSession) -> dict:
    """Confirm or update extracted data."""
    result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.user_id == user_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc.extracted_data = json.dumps(extracted_data)
    doc.status = "confirmed"
    await db.commit()
    await db.refresh(doc)
    return _doc_to_dict(doc)


async def delete_document(doc_id: str, user_id: str, db: AsyncSession) -> dict:
    """Delete a document."""
    result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.user_id == user_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    # Delete file
    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    await db.delete(doc)
    await db.commit()
    return {"id": doc_id, "status": "deleted"}


def _doc_to_dict(doc: Document) -> dict:
    return {
        "id": doc.id,
        "filename": doc.filename,
        "doc_type": doc.doc_type,
        "status": doc.status,
        "extracted_data": json.loads(doc.extracted_data) if doc.extracted_data else None,
        "created_at": str(doc.created_at) if doc.created_at else None,
    }
