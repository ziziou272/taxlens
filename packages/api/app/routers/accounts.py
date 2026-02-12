"""Plaid account linking endpoints."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.services import plaid_service

router = APIRouter()


class ExchangeRequest(BaseModel):
    public_token: str


@router.post("/link")
async def create_link_token(user=Depends(get_current_user)):
    return await plaid_service.create_link_token(user["user_id"])


@router.post("/exchange")
async def exchange_token(body: ExchangeRequest, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await plaid_service.exchange_public_token(user["user_id"], body.public_token, db)


@router.get("")
async def list_accounts(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await plaid_service.list_accounts(user["user_id"], db)


@router.get("/holdings")
async def get_holdings(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await plaid_service.get_holdings(user["user_id"], db)


@router.post("/sync")
async def sync_accounts(user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await plaid_service.sync_accounts(user["user_id"], db)


@router.delete("/{account_id}")
async def disconnect_account(account_id: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await plaid_service.disconnect_account(account_id, user["user_id"], db)
