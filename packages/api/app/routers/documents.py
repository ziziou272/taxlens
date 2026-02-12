"""Document upload and OCR extraction endpoints."""
from fastapi import APIRouter, Depends, UploadFile, File, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_auth
from app.services import document_service, audit_service

router = APIRouter()


class ConfirmRequest(BaseModel):
    extracted_data: dict


@router.post("/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    result = await document_service.upload_document(file, user_id, db)
    await audit_service.log_action(
        db, user_id, "document_upload", "document", result.get("id"),
        ip_address=request.client.host if request.client else None,
    )
    return result


@router.get("")
async def list_documents(user_id: str = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    return await document_service.list_documents(user_id, db)


@router.get("/{doc_id}")
async def get_document(doc_id: str, user_id: str = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    return await document_service.get_document(doc_id, user_id, db)


@router.post("/{doc_id}/confirm")
async def confirm_document(
    doc_id: str,
    body: ConfirmRequest,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    return await document_service.confirm_document(doc_id, user_id, body.extracted_data, db)


@router.delete("/{doc_id}")
async def delete_document(doc_id: str, user_id: str = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    return await document_service.delete_document(doc_id, user_id, db)
