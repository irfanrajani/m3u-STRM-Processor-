"""Main FastAPI application."""

import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings  # instance
from app.core.database import init_db, close_db
from app.api import (
    providers,
    channels,
    vod,
    epg,
    health,
    settings as settings_router,
    auth,
    hdhr,
    system,
    users,
    favorites,
    analytics,
)
from passlib.context import CryptContext
from sqlalchemy import select

# Configure logging - ensure log directory exists BEFORE creating FileHandler
log_file = Path(settings.LOG_FILE)
log_file.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(settings.LOG_FILE), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting IPTV Stream Manager...")
    await init_db()
    logger.info("Database initialized")

    # Create default admin user if it doesn't exist
    from app.core.database import async_session
    from app.models.user import User
    # Password hashing - using argon2 for modern security
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

    async with async_session() as db:
        result = await db.execute(select(User).where(User.username == "admin"))
        admin = result.scalar_one_or_none()
        if not admin:
            admin = User(
                username="admin",
                email="admin@example.com",
                hashed_password=pwd_context.hash("admin123"),
                is_active=True,
                is_superuser=True
            )
            db.add(admin)
            await db.commit()
            logger.info("✅ Created default admin user (admin/admin123)")
        else:
            logger.info("Admin user already exists")

    yield
    logger.info("Shutting down...")
    await close_db()


app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(providers.router, prefix="/api/providers", tags=["providers"])
app.include_router(channels.router, prefix="/api/channels", tags=["channels"])
app.include_router(vod.router, prefix="/api/vod", tags=["vod"])
app.include_router(epg.router, prefix="/api/epg", tags=["epg"])
app.include_router(favorites.router, prefix="/api/favorites", tags=["favorites"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["settings"])
app.include_router(hdhr.router, tags=["hdhr"])


@app.get("/api")
async def api_root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "api_version": "v1",
    }


# Serve React frontend
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Serve the React frontend for all non-API routes."""
    # Check if the path is a file request
    if "." in full_path.split("/")[-1]:
        file_path = Path("/app/frontend/dist") / full_path
        if file_path.is_file():
            return FileResponse(file_path)
    # Otherwise, serve index.html for client-side routing
    return FileResponse("/app/frontend/dist/index.html")
