"""Tax return service — PDF upload + Gemini Vision extraction + Supabase persistence."""
from __future__ import annotations

import base64
import io
import json
import os
import re
import tempfile
import uuid
from typing import Any

from fastapi import HTTPException, UploadFile
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.tax_return import TaxReturn

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = {"application/pdf", "image/jpeg", "image/png", "image/jpg"}

GEMINI_MODEL = "gemini-2.0-flash"

EXTRACTION_PROMPT = """You are an expert at reading IRS Form 1040 tax returns.
Extract the following fields from this tax document and return ONLY valid JSON.
If a field is not present or not readable, use null.

Required JSON structure:
{
  "tax_year": <4-digit year integer, e.g. 2024 — look at the form header>,
  "filing_status": "<Single|Married filing jointly|Married filing separately|Head of household|Qualifying surviving spouse|null>",
  "total_income": <Line 9 dollar amount as float, no commas>,
  "adjusted_gross_income": <Line 11 dollar amount as float>,
  "deduction_type": "<standard|itemized|null>",
  "deduction_amount": <Line 12 dollar amount as float>,
  "taxable_income": <Line 15 dollar amount as float>,
  "total_tax": <Line 24 dollar amount as float>,
  "total_credits": <Sum of lines 19+20+21 as float, or null if not present>,
  "federal_withheld": <Line 25a dollar amount as float>,
  "refund_or_owed": <Line 34 as positive float for refund, or Line 37 as NEGATIVE float for amount owed>,
  "schedule_data": {
    "schedule_c_net_profit": <Schedule C Line 31 net profit/loss, null if not filed>,
    "schedule_d_net_gain": <Schedule D Line 16 net gain/loss, null if not filed>,
    "schedule_e_net_income": <Schedule E total rental/royalty income, null if not filed>
  },
  "confidence_notes": "<brief note about any fields that were hard to read or ambiguous>"
}

Look carefully at all pages. The 1040 is typically 2 pages plus schedules."""


# ---------------------------------------------------------------------------
# Field-level confidence estimation
# ---------------------------------------------------------------------------

KEY_NUMERIC_FIELDS = [
    "total_income",
    "adjusted_gross_income",
    "taxable_income",
    "total_tax",
    "federal_withheld",
    "refund_or_owed",
]


def _estimate_confidence(extracted: dict[str, Any]) -> tuple[float, list[str]]:
    """Estimate overall confidence and return list of fields needing review."""
    needs_review: list[str] = []
    present = 0

    for field in KEY_NUMERIC_FIELDS:
        if extracted.get(field) is not None:
            present += 1
        else:
            needs_review.append(field)

    # Filing status and tax_year are critical
    if not extracted.get("filing_status"):
        needs_review.append("filing_status")
    if not extracted.get("tax_year"):
        needs_review.append("tax_year")

    confidence = present / len(KEY_NUMERIC_FIELDS)
    # Penalise if we couldn't get filing status or year
    if not extracted.get("filing_status"):
        confidence *= 0.9
    if not extracted.get("tax_year"):
        confidence *= 0.8

    return round(confidence, 3), needs_review


# ---------------------------------------------------------------------------
# Gemini Vision extraction
# ---------------------------------------------------------------------------

async def _extract_with_gemini(file_bytes: bytes, mime_type: str) -> dict[str, Any]:
    """Send document to Gemini Vision and return extracted fields dict."""
    import google.generativeai as genai

    api_key = os.environ.get("GEMINI_API_KEY") or settings.__dict__.get("gemini_api_key", "")
    if not api_key:
        raise HTTPException(status_code=503, detail="Gemini API key not configured")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_MODEL)

    # For PDFs, convert to images first using PyMuPDF; for images pass directly
    if mime_type == "application/pdf":
        images = _pdf_to_images(file_bytes)
        parts: list[Any] = []
        for img_bytes in images:
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(img_bytes).decode("utf-8"),
                }
            })
        parts.append(EXTRACTION_PROMPT)
    else:
        parts = [
            {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": base64.b64encode(file_bytes).decode("utf-8"),
                }
            },
            EXTRACTION_PROMPT,
        ]

    response = model.generate_content(parts)
    raw_text = response.text

    # Parse JSON from response
    extracted = _parse_json_from_response(raw_text)
    return extracted


def _pdf_to_images(pdf_bytes: bytes) -> list[bytes]:
    """Convert PDF pages to JPEG images using PyMuPDF (fitz)."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="PyMuPDF not installed. PDF conversion unavailable.",
        )

    images = []
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        # Limit to first 4 pages (1040 is 2 pages + common schedules)
        for page_num in range(min(len(doc), 4)):
            page = doc.load_page(page_num)
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR quality
            pix = page.get_pixmap(matrix=mat)
            img_bytes = pix.tobytes("jpeg")
            images.append(img_bytes)

    return images


def _parse_json_from_response(text: str) -> dict[str, Any]:
    """Extract JSON from Gemini response text."""
    # Try direct parse first
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Try to extract JSON block from markdown
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find any JSON object in the text
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Return raw text wrapped if all else fails
    return {"raw_text": text, "parse_error": True}


# ---------------------------------------------------------------------------
# Service functions
# ---------------------------------------------------------------------------

async def upload_and_extract(file: UploadFile, user_id: str, db: AsyncSession) -> dict[str, Any]:
    """
    Accept a PDF/image upload, run Gemini extraction, return unconfirmed result.
    Does NOT save to DB yet — caller must confirm via confirm_tax_return().
    """
    content_type = file.content_type or ""
    if content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {content_type}")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large. Max size is 10 MB.")

    if len(file_bytes) < 100:
        raise HTTPException(status_code=400, detail="File appears empty or corrupted.")

    # Save file temporarily for storage path tracking
    upload_dir = settings.upload_dir
    os.makedirs(upload_dir, exist_ok=True)
    extraction_id = str(uuid.uuid4())
    ext = "pdf" if content_type == "application/pdf" else content_type.split("/")[-1]
    saved_filename = f"tax_return_{extraction_id}.{ext}"
    saved_path = os.path.join(upload_dir, saved_filename)

    with open(saved_path, "wb") as f:
        f.write(file_bytes)

    # Run Gemini extraction
    try:
        extracted = await _extract_with_gemini(file_bytes, content_type)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

    # Estimate confidence
    confidence, needs_review = _estimate_confidence(extracted)

    # Pull out schedule_data sub-dict
    schedule_data = extracted.pop("schedule_data", None)
    confidence_notes = extracted.pop("confidence_notes", None)

    # Build fields dict (map extracted keys to schema)
    fields = {
        "tax_year": extracted.get("tax_year") or 2024,
        "filing_status": extracted.get("filing_status"),
        "total_income": extracted.get("total_income"),
        "adjusted_gross_income": extracted.get("adjusted_gross_income"),
        "deduction_type": extracted.get("deduction_type"),
        "deduction_amount": extracted.get("deduction_amount"),
        "taxable_income": extracted.get("taxable_income"),
        "total_tax": extracted.get("total_tax"),
        "total_credits": extracted.get("total_credits"),
        "federal_withheld": extracted.get("federal_withheld"),
        "refund_or_owed": extracted.get("refund_or_owed"),
        "schedule_data": schedule_data,
    }

    return {
        "extraction_id": extraction_id,
        "tax_year": fields["tax_year"],
        "source": "pdf_upload",
        "fields": fields,
        "extraction_confidence": confidence,
        "raw_extracted_data": {**extracted, "confidence_notes": confidence_notes},
        "needs_review": needs_review,
        "_pdf_path": saved_path,  # internal, used by confirm
    }


async def confirm_tax_return(
    extraction_id: str,
    fields: dict[str, Any],
    source: str,
    user_id: str,
    pdf_path: str | None,
    db: AsyncSession,
) -> dict[str, Any]:
    """
    User has confirmed (and optionally corrected) extracted data.
    Save to local DB (and optionally Supabase).
    """
    tax_year = fields.get("tax_year")
    if not tax_year:
        raise HTTPException(status_code=400, detail="tax_year is required")

    # Upsert: check if record already exists for this user+year
    result = await db.execute(
        select(TaxReturn).where(
            and_(TaxReturn.user_id == user_id, TaxReturn.tax_year == tax_year)
        )
    )
    existing = result.scalar_one_or_none()

    schedule_data = fields.get("schedule_data")

    if existing:
        tr = existing
    else:
        tr = TaxReturn(id=extraction_id, user_id=user_id)
        db.add(tr)

    tr.tax_year = tax_year
    tr.source = source
    tr.filing_status = fields.get("filing_status")
    tr.total_income = fields.get("total_income")
    tr.adjusted_gross_income = fields.get("adjusted_gross_income")
    tr.deduction_type = fields.get("deduction_type")
    tr.deduction_amount = fields.get("deduction_amount")
    tr.taxable_income = fields.get("taxable_income")
    tr.total_tax = fields.get("total_tax")
    tr.total_credits = fields.get("total_credits")
    tr.federal_withheld = fields.get("federal_withheld")
    tr.refund_or_owed = fields.get("refund_or_owed")
    tr.schedule_data = json.dumps(schedule_data) if schedule_data else None
    tr.pdf_storage_path = pdf_path
    tr.user_confirmed = True

    await db.commit()
    await db.refresh(tr)

    # Also persist to Supabase if service key is configured
    if settings.supabase_url and settings.supabase_service_key:
        try:
            await _upsert_supabase(tr, user_id)
        except Exception:
            pass  # Supabase write is best-effort; local DB is source of truth for now

    return _tr_to_dict(tr)


async def _upsert_supabase(tr: TaxReturn, user_id: str) -> None:
    """Write confirmed tax return to Supabase tax_returns table via REST API."""
    import httpx

    url = f"{settings.supabase_url}/rest/v1/tax_returns"
    headers = {
        "apikey": settings.supabase_service_key,
        "Authorization": f"Bearer {settings.supabase_service_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }
    payload = {
        "user_id": user_id,
        "tax_year": tr.tax_year,
        "source": tr.source,
        "filing_status": tr.filing_status,
        "total_income": tr.total_income,
        "adjusted_gross_income": tr.adjusted_gross_income,
        "deduction_type": tr.deduction_type,
        "deduction_amount": tr.deduction_amount,
        "taxable_income": tr.taxable_income,
        "total_tax": tr.total_tax,
        "total_credits": tr.total_credits,
        "federal_withheld": tr.federal_withheld,
        "refund_or_owed": tr.refund_or_owed,
        "schedule_data": json.loads(tr.schedule_data) if tr.schedule_data else None,
        "raw_extracted_data": json.loads(tr.raw_extracted_data) if tr.raw_extracted_data else None,
        "pdf_storage_path": tr.pdf_storage_path,
        "extraction_confidence": tr.extraction_confidence,
        "user_confirmed": tr.user_confirmed,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        await client.post(url, headers=headers, json=payload)


async def get_tax_return(tax_year: int, user_id: str, db: AsyncSession) -> dict[str, Any]:
    """Get a specific year's tax return for a user."""
    result = await db.execute(
        select(TaxReturn).where(
            and_(TaxReturn.user_id == user_id, TaxReturn.tax_year == tax_year)
        )
    )
    tr = result.scalar_one_or_none()
    if not tr:
        raise HTTPException(status_code=404, detail=f"No tax return found for year {tax_year}")
    return _tr_to_dict(tr)


async def list_tax_returns(user_id: str, db: AsyncSession) -> list[dict[str, Any]]:
    """List all tax returns (summary) for a user."""
    result = await db.execute(
        select(TaxReturn)
        .where(TaxReturn.user_id == user_id)
        .order_by(TaxReturn.tax_year.desc())
    )
    return [_tr_summary(tr) for tr in result.scalars().all()]


async def delete_tax_return(tax_year: int, user_id: str, db: AsyncSession) -> dict[str, Any]:
    """Delete a tax return for a given year."""
    result = await db.execute(
        select(TaxReturn).where(
            and_(TaxReturn.user_id == user_id, TaxReturn.tax_year == tax_year)
        )
    )
    tr = result.scalar_one_or_none()
    if not tr:
        raise HTTPException(status_code=404, detail=f"No tax return found for year {tax_year}")

    # Clean up stored PDF
    if tr.pdf_storage_path and os.path.exists(tr.pdf_storage_path):
        try:
            os.remove(tr.pdf_storage_path)
        except OSError:
            pass

    await db.delete(tr)
    await db.commit()
    return {"tax_year": tax_year, "status": "deleted"}


# ---------------------------------------------------------------------------
# Serialisation helpers
# ---------------------------------------------------------------------------

def _tr_to_dict(tr: TaxReturn) -> dict[str, Any]:
    schedule = json.loads(tr.schedule_data) if tr.schedule_data else None
    raw = json.loads(tr.raw_extracted_data) if tr.raw_extracted_data else None
    return {
        "id": tr.id,
        "user_id": tr.user_id,
        "tax_year": tr.tax_year,
        "source": tr.source,
        "filing_status": tr.filing_status,
        "total_income": tr.total_income,
        "adjusted_gross_income": tr.adjusted_gross_income,
        "deduction_type": tr.deduction_type,
        "deduction_amount": tr.deduction_amount,
        "taxable_income": tr.taxable_income,
        "total_tax": tr.total_tax,
        "total_credits": tr.total_credits,
        "federal_withheld": tr.federal_withheld,
        "refund_or_owed": tr.refund_or_owed,
        "schedule_data": schedule,
        "raw_extracted_data": raw,
        "pdf_storage_path": tr.pdf_storage_path,
        "extraction_confidence": tr.extraction_confidence,
        "user_confirmed": tr.user_confirmed,
        "created_at": str(tr.created_at) if tr.created_at else None,
        "updated_at": str(tr.updated_at) if tr.updated_at else None,
    }


def _tr_summary(tr: TaxReturn) -> dict[str, Any]:
    return {
        "tax_year": tr.tax_year,
        "source": tr.source,
        "user_confirmed": tr.user_confirmed,
        "adjusted_gross_income": tr.adjusted_gross_income,
        "total_tax": tr.total_tax,
        "refund_or_owed": tr.refund_or_owed,
        "extraction_confidence": tr.extraction_confidence,
    }
