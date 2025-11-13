"""First-run setup endpoints."""
import logging
import secrets
import string
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

from app.core.database import get_db
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class SetupStatus(BaseModel):
    """Setup status response."""
    setup_complete: bool
    admin_exists: bool
    message: str


class InitialSetupRequest(BaseModel):
    """Initial setup request."""
    admin_username: str = "admin"
    admin_email: EmailStr = "admin@localhost"
    admin_password: str  # User can provide or we auto-generate


@router.get("/status", response_model=SetupStatus)
async def get_setup_status(db: AsyncSession = Depends(get_db)):
    """
    Check if initial setup is complete.

    Returns:
        setup_complete: True if admin user exists
        admin_exists: True if admin user exists
        message: Status message
    """
    # Check if admin user exists
    result = await db.execute(
        select(User).where(User.username == "admin")
    )
    admin = result.scalar_one_or_none()

    if admin:
        return SetupStatus(
            setup_complete=True,
            admin_exists=True,
            message="Setup already complete"
        )

    return SetupStatus(
        setup_complete=False,
        admin_exists=False,
        message="Initial setup required"
    )


def generate_secure_password(length: int = 16) -> str:
    """
    Generate a secure random password.

    Args:
        length: Password length (default: 16)

    Returns:
        Secure random password
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    # Ensure at least one of each character type
    password = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*")
    ]
    # Fill the rest randomly
    password += [secrets.choice(alphabet) for _ in range(length - 4)]
    # Shuffle
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)


@router.post("/initialize")
async def initialize_setup(
    request: InitialSetupRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Complete initial setup.

    Creates admin user with provided or auto-generated password.
    Only works if no admin user exists.

    Returns:
        Admin credentials and setup status
    """
    # Check if admin already exists
    result = await db.execute(
        select(User).where(User.username == "admin")
    )
    admin = result.scalar_one_or_none()

    if admin:
        raise HTTPException(
            status_code=400,
            detail="Setup already complete. Admin user exists."
        )

    # Use provided password or generate one
    admin_password = request.admin_password or generate_secure_password()

    # Create admin user
    admin = User(
        username=request.admin_username,
        email=request.admin_email,
        hashed_password=pwd_context.hash(admin_password),
        is_active=True,
        is_superuser=True,
        must_change_password=False  # They just set it
    )
    db.add(admin)

    try:
        await db.commit()
        await db.refresh(admin)

        logger.info(f"✅ Initial setup complete - Admin user created: {admin.username}")

        return {
            "status": "success",
            "message": "Initial setup complete",
            "credentials": {
                "username": admin.username,
                "password": admin_password,  # Return password ONLY on initial setup
                "email": admin.email
            },
            "warning": "⚠️ SAVE THESE CREDENTIALS! This is the only time the password will be shown."
        }

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create admin user: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create admin user: {str(e)}"
        )


@router.get("/default-credentials")
async def get_default_credentials(db: AsyncSession = Depends(get_db)):
    """
    Get default credentials info (only if setup not complete).

    Returns default username and that password needs to be set.
    """
    # Check if setup complete
    result = await db.execute(
        select(User).where(User.username == "admin")
    )
    admin = result.scalar_one_or_none()

    if admin:
        raise HTTPException(
            status_code=400,
            detail="Setup already complete"
        )

    return {
        "default_username": "admin",
        "default_email": "admin@localhost",
        "password_note": "You can set your own password or we'll generate a secure one"
    }
