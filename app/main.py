# Entry point for the FastAPI application.
# Registers routers and configures the app instance.

from fastapi import FastAPI

from app.api.routes_health import router as health_router
from app.api.routes_chat import router as chat_router
from app.api.routes_documents import router as documents_router
from app.api.routes_collections import router as collections_router
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(collections_router)
