"""Application settings via pydantic-settings."""
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "TaxLens API"
    version: str = "0.1.0"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./taxlens.db"

    # Plaid
    plaid_client_id: str = ""
    plaid_secret: str = ""
    plaid_env: str = "sandbox"

    # Anthropic (document OCR + AI advisor)
    anthropic_api_key: str = ""

    # File uploads
    upload_dir: str = "./uploads"

    # Supabase Auth
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_key: str = ""
    supabase_jwt_secret: str = ""

    @property
    def auth_enabled(self) -> bool:
        """Auth is enabled when JWT secret is configured."""
        return bool(self.supabase_jwt_secret)

    model_config = {"env_prefix": "TAXLENS_"}


settings = Settings()
