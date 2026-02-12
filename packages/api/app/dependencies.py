"""Shared dependencies."""
from app.database import get_db  # noqa: F401


async def get_current_user():
    """Stub for future auth. Returns a placeholder user id."""
    return {"user_id": "anonymous"}
