"""User schemas."""
from typing import Optional
from pydantic import BaseModel


class UserResponse(BaseModel):
    id: str
    supabase_user_id: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    created_at: Optional[str] = None


class UserUpdateRequest(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
