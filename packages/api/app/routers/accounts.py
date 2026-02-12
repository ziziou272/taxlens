"""Plaid account linking endpoints."""
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_auth
from app.services import plaid_service, audit_service

router = APIRouter()


class ExchangeRequest(BaseModel):
    public_token: str


@router.post("/link")
async def create_link_token(user_id: str = Depends(require_auth)):
    return await plaid_service.create_link_token(user_id)


@router.post("/exchange")
async def exchange_token(
    body: ExchangeRequest,
    request: Request,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    result = await plaid_service.exchange_public_token(user_id, body.public_token, db)
    await audit_service.log_action(
        db, user_id, "plaid_link", "plaid_item", result.get("item_id"),
        ip_address=request.client.host if request.client else None,
    )
    return result


@router.get("")
async def list_accounts(user_id: str = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    return await plaid_service.list_accounts(user_id, db)


@router.get("/holdings")
async def get_holdings(user_id: str = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    return await plaid_service.get_holdings(user_id, db)


@router.post("/sync")
async def sync_accounts(user_id: str = Depends(require_auth), db: AsyncSession = Depends(get_db)):
    return await plaid_service.sync_accounts(user_id, db)


@router.delete("/{account_id}")
async def disconnect_account(
    account_id: str, user_id: str = Depends(require_auth), db: AsyncSession = Depends(get_db)
):
    return await plaid_service.disconnect_account(account_id, user_id, db)
