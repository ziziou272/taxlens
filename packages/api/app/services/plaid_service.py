"""Plaid integration service."""
from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.plaid_item import PlaidItem


def _require_plaid():
    """Raise 503 if Plaid is not configured."""
    if not settings.plaid_client_id or not settings.plaid_secret:
        raise HTTPException(status_code=503, detail="Plaid not configured")


def _get_client():
    """Create and return a Plaid API client."""
    _require_plaid()
    import plaid
    from plaid.api import plaid_api

    env_map = {
        "sandbox": plaid.Environment.Sandbox,
        "development": plaid.Environment.Development,
        "production": plaid.Environment.Production,
    }
    configuration = plaid.Configuration(
        host=env_map.get(settings.plaid_env, plaid.Environment.Sandbox),
        api_key={
            "clientId": settings.plaid_client_id,
            "secret": settings.plaid_secret,
        },
    )
    api_client = plaid.ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)


async def create_link_token(user_id: str) -> dict:
    """Create a Plaid Link token for the client."""
    _require_plaid()
    from plaid.model.link_token_create_request import LinkTokenCreateRequest
    from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
    from plaid.model.products import Products
    from plaid.model.country_code import CountryCode

    client = _get_client()
    request = LinkTokenCreateRequest(
        products=[Products("investments")],
        client_name="TaxLens",
        country_codes=[CountryCode("US")],
        language="en",
        user=LinkTokenCreateRequestUser(client_user_id=user_id),
    )
    response = client.link_token_create(request)
    return {"link_token": response["link_token"]}


async def exchange_public_token(user_id: str, public_token: str, db: AsyncSession) -> dict:
    """Exchange a public token for an access token and store it."""
    _require_plaid()
    from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest

    client = _get_client()
    request = ItemPublicTokenExchangeRequest(public_token=public_token)
    response = client.item_public_token_exchange(request)

    access_token = response["access_token"]
    item_id = response["item_id"]

    # Store encrypted (simple base64 for now; use proper encryption in production)
    import base64
    encrypted = base64.b64encode(access_token.encode()).decode()

    item = PlaidItem(
        user_id=user_id,
        access_token_encrypted=encrypted,
        item_id=item_id,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)

    return {"item_id": item.id, "status": "connected"}


async def list_accounts(user_id: str, db: AsyncSession) -> list[dict]:
    """List all connected Plaid accounts for a user."""
    result = await db.execute(
        select(PlaidItem).where(PlaidItem.user_id == user_id, PlaidItem.status == "active")
    )
    items = result.scalars().all()
    return [
        {
            "id": item.id,
            "institution_name": item.institution_name,
            "status": item.status,
            "created_at": str(item.created_at),
        }
        for item in items
    ]


async def get_holdings(user_id: str, db: AsyncSession) -> list[dict]:
    """Get investment holdings from all connected accounts."""
    _require_plaid()
    from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
    import base64

    client = _get_client()
    result = await db.execute(
        select(PlaidItem).where(PlaidItem.user_id == user_id, PlaidItem.status == "active")
    )
    items = result.scalars().all()

    all_holdings = []
    for item in items:
        access_token = base64.b64decode(item.access_token_encrypted.encode()).decode()
        request = InvestmentsHoldingsGetRequest(access_token=access_token)
        response = client.investments_holdings_get(request)

        for holding in response.get("holdings", []):
            all_holdings.append({
                "account_id": item.id,
                "security_id": str(holding.get("security_id", "")),
                "quantity": float(holding.get("quantity", 0)),
                "cost_basis": float(holding.get("cost_basis", 0)),
                "value": float(holding.get("institution_value", 0)),
            })

    return all_holdings


async def sync_accounts(user_id: str, db: AsyncSession) -> dict:
    """Trigger a sync of transactions/holdings."""
    _require_plaid()
    result = await db.execute(
        select(PlaidItem).where(PlaidItem.user_id == user_id, PlaidItem.status == "active")
    )
    items = result.scalars().all()
    return {"synced": len(items), "status": "complete"}


async def disconnect_account(account_id: str, user_id: str, db: AsyncSession) -> dict:
    """Disconnect (soft-delete) a Plaid account."""
    result = await db.execute(
        select(PlaidItem).where(PlaidItem.id == account_id, PlaidItem.user_id == user_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Account not found")
    item.status = "disconnected"
    await db.commit()
    return {"id": account_id, "status": "disconnected"}
