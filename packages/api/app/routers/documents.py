"""Document endpoints (stub)."""
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/upload")
async def upload_document():
    """Upload placeholder — not yet implemented."""
    raise HTTPException(status_code=501, detail="Document upload not yet implemented")
