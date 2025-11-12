"""Database configuration and session management."""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Create async engine with optimized pool settings
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,
    connect_args={
        "server_settings": {
            "application_name": "iptv_manager",
            "statement_timeout": "30000",  # 30 second query timeout
        }
    }
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Create declarative base
Base = declarative_base()

# Export async_session for use in main.py
from sqlalchemy.ext.asyncio import async_sessionmaker

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the async session factory for use outside FastAPI deps (e.g., Celery).

    Celery tasks import this to create DB sessions without relying on the
    request-scoped dependency injection used by FastAPI endpoints.
    """
    return AsyncSessionLocal


async def get_db():
    """Dependency for getting async database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database.

    We deliberately do NOT call ``Base.metadata.create_all`` here to avoid schema drift
    or accidental creation of tables that are supposed to be managed exclusively by
    Alembic migrations. The Docker entrypoint already runs ``alembic upgrade head``.

    If you ever need an emergency fallback in a dev environment, set the environment
    variable ``FALLBACK_CREATE_ALL=1`` and this function will create any missing tables.
    This should never be used in production; rely on proper migration generation instead.
    """
    if settings.DEBUG and os.getenv("FALLBACK_CREATE_ALL") == "1":
        from logging import getLogger
        log = getLogger(__name__)
        log.warning("FALLBACK_CREATE_ALL=1 detected – running Base.metadata.create_all (DEV ONLY)")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections."""
    await engine.dispose()
