from fastapi import FastAPI

from app.api.routes_collections import router as collections_router
from app.api.routes_health import router as health_router
from app.core.config import get_settings
from app.core.logging import configure_logging

configure_logging()

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="API genérica de Agentic RAG para documentação técnica.",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(collections_router)
