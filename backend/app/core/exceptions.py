"""Custom exceptions and error handlers."""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)


class IPTVManagerException(Exception):
    """Base exception for IPTV Manager."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ProviderError(IPTVManagerException):
    """Provider-related error."""

    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST)


class ChannelNotFoundError(IPTVManagerException):
    """Channel not found error."""

    def __init__(self, channel_id: int):
        super().__init__(
            f"Channel with ID {channel_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class VODNotFoundError(IPTVManagerException):
    """VOD content not found error."""

    def __init__(self, vod_id: int, vod_type: str = "content"):
        super().__init__(
            f"VOD {vod_type} with ID {vod_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class AuthenticationError(IPTVManagerException):
    """Authentication error."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(IPTVManagerException):
    """Authorization error."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)


async def iptv_exception_handler(request: Request, exc: IPTVManagerException):
    """Handle custom IPTV Manager exceptions."""
    logger.error(f"IPTV Manager error: {exc.message}", exc_info=exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
                "status_code": exc.status_code
            }
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with standardized format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "type": "HTTPException",
                "status_code": exc.status_code
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with standardized format."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "message": "Validation error",
                "type": "ValidationError",
                "status_code": 422,
                "details": errors
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "Internal server error",
                "type": "InternalServerError",
                "status_code": 500
            }
        }
    )
