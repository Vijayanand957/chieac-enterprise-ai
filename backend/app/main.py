"""FastAPI application entrypoint: wires up middleware, routers, and startup
tasks for the Enterprise AI Operations Assistant."""
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_analytics, routes_chat, routes_documents
from app.config import get_settings
from app.database import init_models

settings = get_settings()
log = structlog.get_logger()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="RAG + multi-agent + predictive analytics platform for operational decision support.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_chat.router, prefix=settings.api_v1_prefix)
app.include_router(routes_documents.router, prefix=settings.api_v1_prefix)
app.include_router(routes_analytics.router, prefix=settings.api_v1_prefix)


@app.on_event("startup")
async def on_startup() -> None:
    await init_models()
    log.info("startup_complete", environment=settings.environment)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": settings.app_name, "environment": settings.environment}
