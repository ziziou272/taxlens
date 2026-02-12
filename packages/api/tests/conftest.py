"""Test fixtures."""
import pytest
from unittest.mock import patch
from jose import jwt
from httpx import ASGITransport, AsyncClient

from app.database import Base, engine, init_db
from app.main import app

TEST_JWT_SECRET = "test-jwt-secret-for-testing-only"
TEST_USER_ID = "test-user-123"
TEST_USER_ID_B = "test-user-456"


def _make_token(sub: str = TEST_USER_ID, secret: str = TEST_JWT_SECRET) -> str:
    """Create a valid test JWT."""
    return jwt.encode(
        {"sub": sub, "aud": "authenticated", "exp": 9999999999},
        secret,
        algorithm="HS256",
    )


@pytest.fixture(autouse=True)
async def _setup_db():
    """Drop and recreate all tables before each test for a clean state."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture
def auth_settings():
    """Patch settings to enable auth with test secret."""
    with patch("app.dependencies.settings") as mock_settings:
        mock_settings.supabase_jwt_secret = TEST_JWT_SECRET
        mock_settings.auth_enabled = True
        yield mock_settings


@pytest.fixture
def no_auth_settings():
    """Patch settings to disable auth (anonymous mode)."""
    with patch("app.dependencies.settings") as mock_settings:
        mock_settings.supabase_jwt_secret = ""
        mock_settings.auth_enabled = False
        yield mock_settings


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def auth_headers():
    """Authorization headers with valid test token."""
    return {"Authorization": f"Bearer {_make_token()}"}


@pytest.fixture
def auth_headers_b():
    """Authorization headers for a second user."""
    return {"Authorization": f"Bearer {_make_token(sub=TEST_USER_ID_B)}"}
