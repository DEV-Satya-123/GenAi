"""Secure error handling - don't expose sensitive information"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors without exposing internal details"""
    logger.warning(f"Validation error: {exc.errors()}")
    
    # Sanitize error messages
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Invalid input data",
            "details": errors
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle generic exceptions without exposing stack traces"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    # Don't expose internal error details to users
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": id(request)  # For support tracking
        }
    )


async def http_exception_handler(request: Request, exc):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )
