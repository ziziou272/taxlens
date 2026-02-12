"""User management endpoints."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_auth
from app.services import user_service, audit_service

router = APIRouter()


class UserUpdateRequest(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    supabase_user_id: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    created_at: Optional[str] = None


class AuditLogResponse(BaseModel):
    id: str
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: Optional[str] = None


@router.get("/me", response_model=UserResponse)
async def get_me(
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    user = await user_service.get_or_create_user(user_id, db)
    return UserResponse(
        id=user.id,
        supabase_user_id=user.supabase_user_id,
        email=user.email,
        name=user.name,
        created_at=str(user.created_at) if user.created_at else None,
    )


@router.patch("/me", response_model=UserResponse)
async def update_me(
    body: UserUpdateRequest,
    request: Request,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    data = body.model_dump(exclude_unset=True)
    user = await user_service.update_user(user_id, data, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await audit_service.log_action(
        db, user_id, "profile_update", "user", user.id,
        ip_address=request.client.host if request.client else None,
    )
    return UserResponse(
        id=user.id,
        supabase_user_id=user.supabase_user_id,
        email=user.email,
        name=user.name,
        created_at=str(user.created_at) if user.created_at else None,
    )


@router.delete("/me")
async def delete_me(
    request: Request,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    # Log before deletion
    await audit_service.log_action(
        db, user_id, "account_deletion", "user", user_id,
        ip_address=request.client.host if request.client else None,
    )
    deleted = await user_service.delete_user_and_data(user_id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "deleted"}


@router.get("/me/sessions")
async def list_sessions(user_id: str = Depends(require_auth)):
    """List active sessions. Supabase manages sessions — this is informational."""
    return {
        "message": "Session management is handled by Supabase Auth",
        "user_id": user_id,
    }


@router.get("/me/audit-log", response_model=list[AuditLogResponse])
async def get_audit_log(
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    logs = await audit_service.get_user_audit_logs(user_id, db)
    return [
        AuditLogResponse(
            id=log.id,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            details=log.details,
            ip_address=log.ip_address,
            created_at=str(log.created_at) if log.created_at else None,
        )
        for log in logs
    ]
