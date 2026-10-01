"""Centralized application configuration, loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- App ---
    app_name: str = "Enterprise AI Operations Assistant"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    # --- LLM ---
    anthropic_api_key: str = ""
    llm_model: str = "claude-sonnet-4-6"
    llm_max_tokens: int = 2000

    # --- Database ---
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_ops"

    # --- Vector store ---
    vector_store_dir: str = "./data/chroma"
    embedding_model: str = "all-MiniLM-L6-v2"

    # --- ML ---
    model_registry_dir: str = "./models"

    # --- Security ---
    cors_origins: list[str] = ["http://localhost:3000"]
    api_key_header: str = "X-API-Key"
    service_api_key: str = "dev-local-key"


@lru_cache
def get_settings() -> Settings:
    return Settings()
