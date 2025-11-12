"""Main FastAPI application."""

import logging
import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

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
    merge,
    streams as streams_api,
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

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100 per minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting IPTV Stream Manager...")
    await init_db()
    logger.info("Database initialized")
    
    # Create default admin user if it doesn't exist
    from app.core.database import async_session
    from app.models.user import User
    import os
    # Password hashing - using argon2 for modern security
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
    
    # Get admin password from environment or use default (with warning)
    default_admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
    if default_admin_password == "admin123":
        logger.warning("⚠️  Using default admin password! Set DEFAULT_ADMIN_PASSWORD environment variable for production!")
    
    async with async_session() as db:
        result = await db.execute(select(User).where(User.username == "admin"))
        admin = result.scalar_one_or_none()
        if not admin:
            admin = User(
                username="admin",
                email="admin@example.com",
                hashed_password=pwd_context.hash(default_admin_password),
                is_active=True,
                is_superuser=True
            )
            db.add(admin)
            await db.commit()
            logger.info(f"✅ Created default admin user (username: admin)")
            if default_admin_password == "admin123":
                logger.warning("⚠️  SECURITY: Change admin password immediately after first login!")
        else:
            logger.info("Admin user already exists")
    
    yield
    logger.info("Shutting down...")
    await close_db()


app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
app.include_router(merge.router, prefix="/api", tags=["merge"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["settings"])
app.include_router(streams_api.router)
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


# Serve frontend static files - MUST BE LAST
frontend_dist = Path("/app/frontend/dist")
if frontend_dist.exists():
    logger.info(f"Frontend found at {frontend_dist}")
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        # Exclude API and docs from SPA catch-all so real API/doc routes handle them.
        # If a request hits this path with an excluded prefix, respond with 404.
        excluded_prefixes = ("api/", "docs", "openapi.json", "redoc")
        if any(full_path.startswith(prefix) for prefix in excluded_prefixes):
            # Return proper 404 to avoid masking missing API endpoints with 200 JSON
            raise HTTPException(status_code=404, detail={"error": "Not found", "path": full_path})

        file_path = frontend_dist / full_path if full_path else None
        if file_path and file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))

        index_path = frontend_dist / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return {"error": "Frontend not found"}
else:
    logger.warning(f"Frontend not found at {frontend_dist} - serving API only")

    @app.get("/")
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
            "docs": "/docs",
            "note": "Frontend UI not available - API only mode",
        }