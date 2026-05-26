# Application settings loaded from environment variables via pydantic-settings.

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


settings = Settings()
