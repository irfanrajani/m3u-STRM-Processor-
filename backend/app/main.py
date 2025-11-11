"""Main FastAPI application."""

import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

# Configure logging - ensure log directory exists
log_file = Path(settings.LOG_FILE)
log_file.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/docs/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Application startup event."""
    logger.info("Application startup")


@app.on_event("shutdown")
async def shutdown():
    """Application shutdown event."""
    logger.info("Application shutdown")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    yield