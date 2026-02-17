"""Tax return endpoints — PDF upload, AI extraction, CRUD for previous-year returns."""
from fastapi import APIRouter, Depends, File, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_auth
from app.schemas.tax_return import (
    TaxReturnConfirmRequest,
    TaxReturnExtractResponse,
    TaxReturnResponse,
    TaxReturnSummary,
)
from app.services import tax_return_service

router = APIRouter()


@router.post("/upload-pdf", response_model=TaxReturnExtractResponse)
async def upload_pdf(
    request: Request,
    file: UploadFile = File(...),
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a 1040 PDF (or image). Gemini Vision extracts key fields.
    Returns extracted data with confidence scores for user review.
    Call POST /confirm to save after review.
    """
    result = await tax_return_service.upload_and_extract(file, user_id, db)

    # Strip internal _pdf_path from response; keep it in session cache via extraction_id
    # For simplicity in MVP we embed pdf_path in raw_extracted_data
    pdf_path = result.pop("_pdf_path", None)
    if result.get("raw_extracted_data") is not None:
        result["raw_extracted_data"]["_pdf_path"] = pdf_path

    return result


@router.post("/confirm", response_model=TaxReturnResponse)
async def confirm_tax_return(
    body: TaxReturnConfirmRequest,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """
    User confirms (and optionally corrects) extracted data.
    Saves the tax return to the database.
    """
    fields_dict = body.fields.model_dump()
    pdf_path = None
    # Recover pdf_path if passed back through raw_extracted_data
    # (The client should pass extraction_id; pdf_path is looked up server-side in production)

    return await tax_return_service.confirm_tax_return(
        extraction_id=body.extraction_id,
        fields=fields_dict,
        source=body.source,
        user_id=user_id,
        pdf_path=pdf_path,
        db=db,
    )


@router.get("", response_model=list[TaxReturnSummary])
async def list_tax_returns(
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List all tax return years for the current user (for year switcher dropdown)."""
    return await tax_return_service.list_tax_returns(user_id, db)


@router.get("/{tax_year}", response_model=TaxReturnResponse)
async def get_tax_return(
    tax_year: int,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get the full tax return for a specific year."""
    return await tax_return_service.get_tax_return(tax_year, user_id, db)


@router.delete("/{tax_year}")
async def delete_tax_return(
    tax_year: int,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Delete a tax return for a specific year."""
    return await tax_return_service.delete_tax_return(tax_year, user_id, db)
