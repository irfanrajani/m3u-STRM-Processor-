"""Database initialization CLI."""
import asyncio
import sys
from sqlalchemy import select
from app.core.database import get_session_factory
from app.core.security import get_password_hash
from app.models.user import User
from app.models.settings import Settings


async def create_admin_user():
    """Create initial admin user."""
    session_factory = get_session_factory()
    async with session_factory() as db:
        # Check if admin exists
        result = await db.execute(
            select(User).where(User.username == "admin")
        )
        admin = result.scalar_one_or_none()

        if admin:
            print("Admin user already exists!")
            return

        # Create admin user
        admin = User(
            username="admin",
            email="admin@localhost",
            hashed_password=get_password_hash("admin"),
            is_active=True,
            is_superuser=True
        )
        db.add(admin)
        await db.commit()

        print("✓ Admin user created successfully!")
        print("  Username: admin")
        print("  Password: admin")
        print("  Please change the password after first login!")


async def create_default_settings():
    """Create default app settings."""
    session_factory = get_session_factory()
    async with session_factory() as db:
        # Check if settings exist
        result = await db.execute(select(Settings))
        existing = result.scalar_one_or_none()

        if existing:
            print("Settings already exist!")
            return

        # Create default settings
        settings = Settings(
            fuzzy_threshold=85,
            health_check_enabled=True,
            health_check_timeout=10,
            health_check_schedule="0 3 * * *",  # 3 AM daily
            sync_schedule="0 * * * *",  # Every hour
            epg_schedule="0 2 * * *",  # 2 AM daily
            enable_hdhr=True,
            hdhr_device_id="IPTV-MGR",
            hdhr_tuner_count=4
        )
        db.add(settings)
        await db.commit()

        print("✓ Default settings created successfully!")


async def init_database():
    """Initialize database with default data."""
    print("Initializing database...")
    await create_admin_user()
    await create_default_settings()
    print("\n✓ Database initialization complete!")


if __name__ == "__main__":
    asyncio.run(init_database())
