"""
Rate Limiting Middleware

Implements token bucket algorithm for API rate limiting.
Uses Redis for distributed rate limiting across multiple instances.
"""

import time
import hashlib
from typing import Optional, Callable, Dict, Any
from datetime import datetime, timedelta

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

try:
    import redis.asyncio as redis
except ImportError:
    redis = None

from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)


class RateLimitExceeded(HTTPException):
    """Custom exception for rate limit exceeded"""

    def __init__(
        self,
        detail: str = "Rate limit exceeded. Please try again later.",
        retry_after: int = 60,
    ):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers={"Retry-After": str(retry_after)},
        )


class TokenBucket:
    """
    Token Bucket Algorithm for Rate Limiting

    Each user gets a bucket with a maximum capacity.
    Tokens are added at a fixed rate.
    Each request consumes a token.
    """

    def __init__(
        self,
        capacity: int,
        refill_rate: float,
        redis_client: Optional[redis.Redis] = None,
    ):
        """
        Args:
            capacity: Maximum number of tokens
            refill_rate: Tokens added per second
            redis_client: Redis client for distributed limiting
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.redis_client = redis_client
        self.local_buckets: Dict[str, Dict[str, Any]] = {}

    async def consume(self, key: str, tokens: int = 1) -> tuple[bool, dict]:
        """
        Try to consume tokens from bucket

        Args:
            key: Identifier (user_id, ip_address, etc.)
            tokens: Number of tokens to consume

        Returns:
            (allowed, info) tuple
            - allowed: Whether request is allowed
            - info: Rate limit information
        """
        if self.redis_client:
            return await self._consume_redis(key, tokens)
        else:
            return await self._consume_local(key, tokens)

    async def _consume_redis(self, key: str, tokens: int) -> tuple[bool, dict]:
        """Redis-based token bucket (distributed)"""
        bucket_key = f"rate_limit:{key}"
        now = time.time()

        # Lua script for atomic operations
        lua_script = """
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local tokens_requested = tonumber(ARGV[3])
        local now = tonumber(ARGV[4])

        local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(bucket[1]) or capacity
        local last_refill = tonumber(bucket[2]) or now

        -- Calculate tokens to add
        local time_passed = now - last_refill
        local tokens_to_add = time_passed * refill_rate
        tokens = math.min(capacity, tokens + tokens_to_add)

        -- Try to consume
        local allowed = 0
        if tokens >= tokens_requested then
            tokens = tokens - tokens_requested
            allowed = 1
        end

        -- Update bucket
        redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
        redis.call('EXPIRE', key, 3600)  -- 1 hour TTL

        return {allowed, tokens, capacity}
        """

        try:
            result = await self.redis_client.eval(
                lua_script,
                1,
                bucket_key,
                self.capacity,
                self.refill_rate,
                tokens,
                now,
            )

            allowed = bool(result[0])
            remaining = int(result[1])
            limit = int(result[2])

            return allowed, {
                "limit": limit,
                "remaining": remaining,
                "reset": int(now + (self.capacity - remaining) / self.refill_rate),
            }

        except Exception as e:
            logger.error(f"Redis rate limit error: {e}")
            # Fail open (allow request) on Redis errors
            return True, {"limit": self.capacity, "remaining": self.capacity, "reset": 0}

    async def _consume_local(self, key: str, tokens: int) -> tuple[bool, dict]:
        """In-memory token bucket (single instance)"""
        now = time.time()

        if key not in self.local_buckets:
            self.local_buckets[key] = {
                "tokens": self.capacity,
                "last_refill": now,
            }

        bucket = self.local_buckets[key]

        # Calculate tokens to add
        time_passed = now - bucket["last_refill"]
        tokens_to_add = time_passed * self.refill_rate
        bucket["tokens"] = min(self.capacity, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = now

        # Try to consume
        allowed = bucket["tokens"] >= tokens
        if allowed:
            bucket["tokens"] -= tokens

        return allowed, {
            "limit": self.capacity,
            "remaining": int(bucket["tokens"]),
            "reset": int(now + (self.capacity - bucket["tokens"]) / self.refill_rate),
        }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI Middleware for Rate Limiting

    Applies different rate limits based on:
    - User authentication status
    - User role
    - API endpoint
    - Subscription tier
    """

    def __init__(
        self,
        app: ASGIApp,
        redis_url: Optional[str] = None,
        default_limit: int = 100,
        default_window: int = 60,
    ):
        super().__init__(app)
        self.default_limit = default_limit
        self.default_window = default_window

        # Initialize Redis client
        if redis_url and redis:
            try:
                self.redis_client = redis.from_url(
                    redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                )
                logger.info("✅ Redis rate limiting enabled")
            except Exception as e:
                logger.warning(f"⚠️ Redis connection failed: {e}. Using in-memory rate limiting.")
                self.redis_client = None
        else:
            self.redis_client = None
            logger.info("ℹ️ Using in-memory rate limiting")

        # Rate limit configurations
        self.rate_limits = {
            # Anonymous users (by IP)
            "anonymous": TokenBucket(capacity=20, refill_rate=20/60, redis_client=self.redis_client),

            # Authenticated users (by user_id)
            "authenticated": TokenBucket(capacity=100, refill_rate=100/60, redis_client=self.redis_client),

            # AI endpoints (expensive operations)
            "ai_endpoint": TokenBucket(capacity=10, refill_rate=10/60, redis_client=self.redis_client),

            # Quantum endpoints (very expensive)
            "quantum_endpoint": TokenBucket(capacity=5, refill_rate=5/300, redis_client=self.redis_client),

            # Subscription tiers
            "tier_community": TokenBucket(capacity=50, refill_rate=50/60, redis_client=self.redis_client),
            "tier_professional": TokenBucket(capacity=200, refill_rate=200/60, redis_client=self.redis_client),
            "tier_enterprise": TokenBucket(capacity=1000, refill_rate=1000/60, redis_client=self.redis_client),
            "tier_quantum_plus": TokenBucket(capacity=5000, refill_rate=5000/60, redis_client=self.redis_client),
        }

    async def dispatch(self, request: Request, call_next: Callable):
        """Process request and apply rate limiting"""

        # Skip rate limiting for health checks and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Determine rate limit bucket
        bucket, key = await self._get_rate_limit_bucket(request)

        # Check rate limit
        allowed, info = await bucket.consume(key)

        # Add rate limit headers to response
        response = None
        if allowed:
            response = await call_next(request)
        else:
            # Rate limit exceeded
            retry_after = info["reset"] - int(time.time())
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(info["reset"])

        return response

    async def _get_rate_limit_bucket(self, request: Request) -> tuple[TokenBucket, str]:
        """
        Determine which rate limit bucket to use

        Returns:
            (bucket, key) tuple
        """
        # Get user from request state (set by auth middleware)
        user = getattr(request.state, "user", None)

        # AI/Quantum endpoint detection
        if "/api/v1/clinical-decision" in request.url.path or "/api/v1/diagnosis" in request.url.path:
            key = f"ai:{user.user_id if user else self._get_client_ip(request)}"
            return self.rate_limits["ai_endpoint"], key

        if "/api/v1/resource-optimization" in request.url.path:
            key = f"quantum:{user.user_id if user else self._get_client_ip(request)}"
            return self.rate_limits["quantum_endpoint"], key

        # Subscription tier based
        if user and hasattr(user, "hospital"):
            tier = user.hospital.subscription_tier.value
            bucket_name = f"tier_{tier}"
            if bucket_name in self.rate_limits:
                return self.rate_limits[bucket_name], f"user:{user.user_id}"

        # Authenticated vs anonymous
        if user:
            return self.rate_limits["authenticated"], f"user:{user.user_id}"
        else:
            ip = self._get_client_ip(request)
            return self.rate_limits["anonymous"], f"ip:{ip}"

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address (handles proxies)"""
        # Check X-Forwarded-For header (for proxies)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct client
        if request.client:
            return request.client.host

        return "unknown"


# ============================================================================
# DECORATOR FOR CUSTOM RATE LIMITS
# ============================================================================

def rate_limit(limit: int, window: int = 60):
    """
    Decorator for custom rate limits on specific endpoints

    Usage:
        @app.get("/expensive-operation")
        @rate_limit(limit=5, window=60)
        async def expensive_operation():
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request from args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                return await func(*args, **kwargs)

            # Apply custom rate limit
            bucket = TokenBucket(capacity=limit, refill_rate=limit/window)

            # Get user or IP
            user = getattr(request.state, "user", None)
            key = f"user:{user.user_id}" if user else f"ip:{request.client.host}"

            allowed, info = await bucket.consume(key)

            if not allowed:
                retry_after = info["reset"] - int(time.time())
                raise RateLimitExceeded(retry_after=retry_after)

            return await func(*args, **kwargs)

        return wrapper
    return decorator


# ============================================================================
# REDIS HELPER FUNCTIONS
# ============================================================================

async def get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client for rate limiting"""
    if not redis:
        return None

    try:
        client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        await client.ping()
        return client
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return None


async def clear_rate_limit(key: str, redis_client: Optional[redis.Redis] = None):
    """Clear rate limit for a specific key (admin function)"""
    if not redis_client:
        return

    try:
        await redis_client.delete(f"rate_limit:{key}")
        logger.info(f"Cleared rate limit for key: {key}")
    except Exception as e:
        logger.error(f"Failed to clear rate limit: {e}")
