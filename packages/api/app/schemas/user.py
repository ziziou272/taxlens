"""User schemas."""
from typing import Optional
from pydantic import BaseModel


class UserResponse(BaseModel):
    id: str
    email: Optional[str] = None
    name: Optional[str] = None
