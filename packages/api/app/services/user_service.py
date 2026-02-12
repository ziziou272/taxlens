"""User management service."""
from __future__ import annotations

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.tax_profile import TaxProfile
from app.models.document import Document
from app.models.scenario import Scenario
from app.models.equity_grant import EquityGrant
from app.models.alert import Alert
from app.models.plaid_item import PlaidItem
from app.models.audit_log import AuditLog


async def get_or_create_user(supabase_user_id: str, db: AsyncSession) -> User:
    """Upsert user by supabase_user_id. Auto-creates on first call."""
    result = await db.execute(
        select(User).where(User.supabase_user_id == supabase_user_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        user = User(supabase_user_id=supabase_user_id)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


async def get_user(supabase_user_id: str, db: AsyncSession) -> User | None:
    result = await db.execute(
        select(User).where(User.supabase_user_id == supabase_user_id)
    )
    return result.scalar_one_or_none()


async def update_user(supabase_user_id: str, data: dict, db: AsyncSession) -> User | None:
    user = await get_or_create_user(supabase_user_id, db)
    for key, value in data.items():
        if hasattr(user, key) and key not in ("id", "supabase_user_id", "created_at"):
            setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user_and_data(supabase_user_id: str, db: AsyncSession) -> bool:
    """Delete user and ALL associated data (CCPA compliance)."""
    user = await get_user(supabase_user_id, db)
    if not user:
        return False

    uid = user.id

    # Get all profile IDs for this user
    profiles = await db.execute(select(TaxProfile.id).where(TaxProfile.user_id == uid))
    profile_ids = [p for p in profiles.scalars().all()]

    # Delete alerts and equity grants by profile
    if profile_ids:
        await db.execute(delete(Alert).where(Alert.profile_id.in_(profile_ids)))
        await db.execute(delete(EquityGrant).where(EquityGrant.profile_id.in_(profile_ids)))

    # Delete by user_id
    await db.execute(delete(TaxProfile).where(TaxProfile.user_id == uid))
    await db.execute(delete(Document).where(Document.user_id == uid))
    await db.execute(delete(Scenario).where(Scenario.user_id == uid))
    await db.execute(delete(PlaidItem).where(PlaidItem.user_id == uid))
    await db.execute(delete(AuditLog).where(AuditLog.user_id == uid))
    await db.delete(user)
    await db.commit()
    return True
