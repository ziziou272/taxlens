"""Document schemas."""
from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    message: str = "Not implemented"
