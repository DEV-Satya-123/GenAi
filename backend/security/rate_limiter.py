"""Rate limiting for API endpoints"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Custom handler for rate limit exceeded"""
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
            "detail": str(exc.detail)
        }
    )


# Rate limit configurations
RATE_LIMITS = {
    "default": "100/minute",
    "clone": "5/minute",
    "run": "10/minute",
    "status": "60/minute",
}
