"""Main FastAPI application."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db, close_db
from app.api import providers, channels, vod, epg, health, settings as settings_router, auth, hdhr, system, users, favorites, analytics

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting IPTV Stream Manager")
    await init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down IPTV Stream Manager")
    await close_db()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Comprehensive IPTV stream management for Emby",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS if not settings.DEBUG else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(favorites.router, prefix="/api/favorites", tags=["favorites"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(providers.router, prefix="/api/providers", tags=["providers"])
app.include_router(channels.router, prefix="/api/channels", tags=["channels"])
app.include_router(vod.router, prefix="/api/vod", tags=["vod"])
app.include_router(epg.router, prefix="/api/epg", tags=["epg"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["settings"])
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(hdhr.router, tags=["hdhr"])  # No prefix - HDHomeRun endpoints at root


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/api/status")
async def status():
    """Get application status."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }
