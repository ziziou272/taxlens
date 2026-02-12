"""Application settings via pydantic-settings."""
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

    model_config = {"env_prefix": "TAXLENS_"}


settings = Settings()
