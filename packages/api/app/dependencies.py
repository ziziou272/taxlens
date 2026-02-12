"""Shared dependencies."""
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings
from app.database import get_db  # noqa: F401

# Optional bearer — does not raise on missing token
_bearer_scheme = HTTPBearer(auto_error=False)


def _decode_token(token: str) -> dict:
    """Decode and validate a Supabase JWT. Returns payload dict."""
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> Optional[str]:
    """Return the authenticated user_id or None.

    When auth is not configured (no JWT secret), always returns ``"anonymous"``
    for backward compatibility with the MVP.
    """
    if not settings.auth_enabled:
        return "anonymous"

    if credentials is None:
        return None

    payload = _decode_token(credentials.credentials)
    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing sub claim",
        )
    return user_id


async def require_auth(
    user_id: Optional[str] = Depends(get_current_user),
) -> str:
    """Dependency that enforces authentication — returns user_id or 401."""
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


async def optional_auth(
    user_id: Optional[str] = Depends(get_current_user),
) -> Optional[str]:
    """Dependency that passes through user_id or None (anonymous OK)."""
    return user_id
