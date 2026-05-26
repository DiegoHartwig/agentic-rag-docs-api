# Application settings loaded from environment variables via pydantic-settings.

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "agentic-docs-rag-api"
    APP_ENV: str = "dev"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""

    EMBEDDING_PROVIDER: str = "fastembed"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_VECTOR_SIZE: int = 384


@lru_cache
def get_settings() -> Settings:
    return Settings()
