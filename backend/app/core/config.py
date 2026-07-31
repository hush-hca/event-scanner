"""Environment-backed application settings."""

from functools import lru_cache

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration sourced exclusively from environment variables."""

    model_config = SettingsConfigDict(env_file=None, env_prefix="EVENTRADAR_", extra="ignore")

    app_name: str = "EventRadar"
    environment: str = Field(default="development", pattern="^(development|test|production)$")
    database_url: str = "postgresql+psycopg://eventradar:eventradar@postgres:5432/eventradar"
    redis_url: str = "redis://redis:6379/0"
    development_webhook_url: HttpUrl | None = None


@lru_cache
def get_settings() -> Settings:
    """Return the cached, validated settings instance."""

    return Settings()
