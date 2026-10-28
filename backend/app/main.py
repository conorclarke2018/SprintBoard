"""SprintBoard FastAPI application entry point."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import models  # noqa: F401  (registers all tables)
from app.config import settings
from app.core.error_handlers import register_exception_handlers
from app.database import Base, engine
from app.logging_config import setup_logging
from app.routers import admin, auth, issues, projects, sprints

FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"

setup_logging(settings.log_level)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(engine)
    logger.info("SprintBoard started")
    yield


app = FastAPI(title="SprintBoard", lifespan=lifespan)
register_exception_handlers(app)

for router in (auth.router, projects.router, issues.router, sprints.router, admin.router):
    app.include_router(router)


@app.get("/api/health")
def health() -> dict[str, str]:
    """Simple check that the API is running."""
    return {"status": "ok"}

if FRONTEND_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa_fallback(full_path: str) -> FileResponse:
        """Return a real file if it exists, otherwise index.html for client-side routes."""
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")
        file = FRONTEND_DIST / full_path
        if full_path and file.is_file() and FRONTEND_DIST in file.resolve().parents:
            return FileResponse(file)
        return FileResponse(FRONTEND_DIST / "index.html")
