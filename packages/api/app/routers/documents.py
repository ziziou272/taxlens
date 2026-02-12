"""Document upload and OCR extraction endpoints."""
from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.services import document_service

router = APIRouter()


class ConfirmRequest(BaseModel):
    extracted_data: dict


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await document_service.upload_document(file, user["user_id"], db)


@router.get("")
async def list_documents(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await document_service.list_documents(user["user_id"], db)


@router.get("/{doc_id}")
async def get_document(doc_id: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await document_service.get_document(doc_id, user["user_id"], db)


@router.post("/{doc_id}/confirm")
async def confirm_document(
    doc_id: str,
    body: ConfirmRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await document_service.confirm_document(doc_id, user["user_id"], body.extracted_data, db)


@router.delete("/{doc_id}")
async def delete_document(doc_id: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await document_service.delete_document(doc_id, user["user_id"], db)
