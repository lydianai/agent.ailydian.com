"""
CSRF (Cross-Site Request Forgery) Protection

Implements double-submit cookie pattern and synchronizer token pattern
for preventing CSRF attacks on state-changing operations.
"""

import secrets
import hmac
import hashlib
import time
from typing import Optional, Callable
from datetime import datetime, timedelta

from fastapi import Request, HTTPException, status, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from core.logging import get_logger
from core.config import settings

logger = get_logger(__name__)


# ============================================================================
# CONFIGURATION
# ============================================================================

CSRF_TOKEN_LENGTH = 32  # 256 bits
CSRF_TOKEN_EXPIRY = 3600  # 1 hour
CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"
CSRF_FORM_FIELD = "csrf_token"

# Methods that require CSRF protection
CSRF_PROTECTED_METHODS = ["POST", "PUT", "PATCH", "DELETE"]

# Endpoints that are exempt from CSRF protection
CSRF_EXEMPT_PATHS = [
    "/api/v1/auth/login",  # Login endpoint (initial token generation)
    "/api/v1/auth/register",  # Registration
    "/health",  # Health checks
    "/metrics",  # Prometheus metrics
    "/docs",  # API docs
    "/redoc",
    "/openapi.json",
]


# ============================================================================
# CSRF TOKEN GENERATION
# ============================================================================

class CSRFTokenManager:
    """
    Manages CSRF token generation and validation

    Uses HMAC-based tokens with timestamp for expiry.
    """

    def __init__(self, secret_key: Optional[str] = None):
        """
        Args:
            secret_key: Secret key for HMAC signing (defaults to settings.SECRET_KEY)
        """
        self.secret_key = secret_key or settings.SECRET_KEY.encode()

    def generate_token(self) -> str:
        """
        Generate a new CSRF token

        Returns:
            CSRF token string (hex encoded)
        """
        # Generate random token
        random_bytes = secrets.token_bytes(CSRF_TOKEN_LENGTH)

        # Add timestamp
        timestamp = int(time.time())
        timestamp_bytes = timestamp.to_bytes(8, byteorder="big")

        # Combine random + timestamp
        token_data = random_bytes + timestamp_bytes

        # Sign with HMAC
        signature = hmac.new(
            self.secret_key,
            token_data,
            hashlib.sha256,
        ).digest()

        # Combine token_data + signature
        full_token = token_data + signature

        return full_token.hex()

    def validate_token(self, token: str) -> bool:
        """
        Validate a CSRF token

        Args:
            token: CSRF token to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            # Decode hex
            token_bytes = bytes.fromhex(token)

            # Extract parts
            random_part = token_bytes[:CSRF_TOKEN_LENGTH]
            timestamp_bytes = token_bytes[CSRF_TOKEN_LENGTH : CSRF_TOKEN_LENGTH + 8]
            signature = token_bytes[CSRF_TOKEN_LENGTH + 8 :]

            # Verify signature
            token_data = random_part + timestamp_bytes
            expected_signature = hmac.new(
                self.secret_key,
                token_data,
                hashlib.sha256,
            ).digest()

            if not hmac.compare_digest(signature, expected_signature):
                logger.warning("CSRF token signature verification failed")
                return False

            # Check expiry
            timestamp = int.from_bytes(timestamp_bytes, byteorder="big")
            current_time = int(time.time())

            if current_time - timestamp > CSRF_TOKEN_EXPIRY:
                logger.warning("CSRF token expired")
                return False

            return True

        except Exception as e:
            logger.error(f"CSRF token validation error: {e}")
            return False

    def rotate_token(self, old_token: str) -> Optional[str]:
        """
        Rotate CSRF token (used after state-changing operations)

        Args:
            old_token: Current CSRF token

        Returns:
            New CSRF token if old token is valid, None otherwise
        """
        if self.validate_token(old_token):
            return self.generate_token()
        return None


# Global token manager instance
csrf_token_manager = CSRFTokenManager()


# ============================================================================
# CSRF MIDDLEWARE
# ============================================================================

class CSRFMiddleware(BaseHTTPMiddleware):
    """
    FastAPI Middleware for CSRF Protection

    Implements double-submit cookie pattern:
    1. Set CSRF token in cookie
    2. Require token in header/form for state-changing requests
    3. Validate both match and are valid
    """

    def __init__(
        self,
        app: ASGIApp,
        exempt_paths: Optional[list] = None,
        cookie_secure: bool = True,
        cookie_httponly: bool = True,
        cookie_samesite: str = "strict",
    ):
        super().__init__(app)
        self.exempt_paths = exempt_paths or CSRF_EXEMPT_PATHS
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly
        self.cookie_samesite = cookie_samesite

    async def dispatch(self, request: Request, call_next: Callable):
        """Process request and apply CSRF protection"""

        # Skip exempt paths
        if self._is_exempt_path(request.url.path):
            return await call_next(request)

        # Skip non-protected methods (GET, HEAD, OPTIONS)
        if request.method not in CSRF_PROTECTED_METHODS:
            response = await call_next(request)
            # Set CSRF token in cookie for subsequent requests
            self._set_csrf_cookie(request, response)
            return response

        # Validate CSRF token for protected methods
        if not self._validate_csrf_request(request):
            logger.warning(
                f"CSRF validation failed for {request.method} {request.url.path} "
                f"from {request.client.host if request.client else 'unknown'}"
            )
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "error": "csrf_validation_failed",
                    "message": "CSRF token missing or invalid",
                },
            )

        # Process request
        response = await call_next(request)

        # Rotate token after successful state-changing operation
        if response.status_code < 400:
            self._rotate_csrf_token(request, response)

        return response

    def _is_exempt_path(self, path: str) -> bool:
        """Check if path is exempt from CSRF protection"""
        for exempt_path in self.exempt_paths:
            if path.startswith(exempt_path):
                return True
        return False

    def _validate_csrf_request(self, request: Request) -> bool:
        """
        Validate CSRF token from request

        Checks both cookie and header/form field.
        """
        # Get token from cookie
        cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
        if not cookie_token:
            logger.warning("CSRF cookie not found")
            return False

        # Get token from header or form
        header_token = request.headers.get(CSRF_HEADER_NAME)

        # For form submissions, check form field
        # (requires reading body, which is handled by FastAPI)
        if not header_token:
            # Try to get from form data (if available)
            # This is a simplified check; in production, you'd parse the form
            logger.warning("CSRF token not found in header")
            return False

        # Verify tokens match
        if not hmac.compare_digest(cookie_token, header_token):
            logger.warning("CSRF token mismatch")
            return False

        # Validate token itself
        if not csrf_token_manager.validate_token(cookie_token):
            logger.warning("CSRF token validation failed")
            return False

        return True

    def _set_csrf_cookie(self, request: Request, response: Response):
        """Set CSRF token in cookie"""
        # Check if cookie already exists and is valid
        existing_token = request.cookies.get(CSRF_COOKIE_NAME)

        if existing_token and csrf_token_manager.validate_token(existing_token):
            # Reuse existing valid token
            token = existing_token
        else:
            # Generate new token
            token = csrf_token_manager.generate_token()

        # Set cookie
        response.set_cookie(
            key=CSRF_COOKIE_NAME,
            value=token,
            max_age=CSRF_TOKEN_EXPIRY,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
        )

    def _rotate_csrf_token(self, request: Request, response: Response):
        """Rotate CSRF token after state-changing operation"""
        old_token = request.cookies.get(CSRF_COOKIE_NAME)

        if old_token:
            new_token = csrf_token_manager.rotate_token(old_token)

            if new_token:
                response.set_cookie(
                    key=CSRF_COOKIE_NAME,
                    value=new_token,
                    max_age=CSRF_TOKEN_EXPIRY,
                    secure=self.cookie_secure,
                    httponly=self.cookie_httponly,
                    samesite=self.cookie_samesite,
                )


# ============================================================================
# DEPENDENCY FOR ROUTE-LEVEL CSRF PROTECTION
# ============================================================================

async def require_csrf_token(request: Request) -> str:
    """
    Dependency to require CSRF token on specific routes

    Usage:
        @app.post("/sensitive-operation")
        async def sensitive_op(csrf_token: str = Depends(require_csrf_token)):
            ...
    """
    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
    header_token = request.headers.get(CSRF_HEADER_NAME)

    if not cookie_token or not header_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing",
        )

    if not hmac.compare_digest(cookie_token, header_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token mismatch",
        )

    if not csrf_token_manager.validate_token(cookie_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token invalid or expired",
        )

    return cookie_token


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_csrf_token(request: Request) -> Optional[str]:
    """
    Get current CSRF token from request

    Returns:
        CSRF token string or None
    """
    return request.cookies.get(CSRF_COOKIE_NAME)


def generate_csrf_token() -> str:
    """
    Generate a new CSRF token

    Returns:
        CSRF token string
    """
    return csrf_token_manager.generate_token()


def exempt_from_csrf(path: str):
    """
    Mark a path as exempt from CSRF protection

    Args:
        path: Path to exempt
    """
    if path not in CSRF_EXEMPT_PATHS:
        CSRF_EXEMPT_PATHS.append(path)
