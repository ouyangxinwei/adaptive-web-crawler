
from fastapi import FastAPI

from backend.app.config import settings
from backend.app.api.routes.fetch import router as fetch_router
from backend.app.api.routes.sources import router as sources_router
from backend.app.api.routes.tasks import router as tasks_router
from backend.app.api.routes.rules import router as rules_router
from backend.app.api.routes.history import router as history_router
from backend.app.api.routes.results import router as results_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="An adaptive web crawling platform powered by Scrapling.",
)


@app.get("/")
async def root():
    return {
        "message": "Adaptive Web Crawler API",
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.app_env,
    }


app.include_router(
    fetch_router,
    prefix="/api/v1",
    tags=["Fetch"],
)

app.include_router(
    sources_router,
    prefix="/api/v1",
    tags=["Sources"],
)

app.include_router(
    tasks_router,
    prefix="/api/v1",
    tags=["Tasks"],
)

app.include_router(
    rules_router,
    prefix="/api/v1",
    tags=["Rules"],
)

app.include_router(
    history_router,
    prefix="/api/v1",
    tags=["History"],
)

app.include_router(
    results_router,
    prefix="/api/v1",
    tags=["Results"],
)