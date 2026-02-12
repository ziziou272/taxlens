"""Application settings via pydantic-settings."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "TaxLens API"
    version: str = "0.1.0"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./taxlens.db"

    model_config = {"env_prefix": "TAXLENS_"}


settings = Settings()
