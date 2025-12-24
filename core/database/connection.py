"""
Database Connection Management

Async database connections with connection pooling.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as aioredis

from core.config import settings
from core.logging import get_logger

logger = get_logger()


# ============================================================================
# POSTGRESQL (Primary Database)
# ============================================================================

# Create async engine
async_engine = create_async_engine(
    settings.postgres_url,
    echo=settings.debug,
    pool_size=settings.postgres_pool_size,
    max_overflow=settings.postgres_max_overflow,
    pool_pre_ping=True,  # Verify connections before using
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session

    Usage in FastAPI:
        @app.get("/patients")
        async def get_patients(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            await session.close()


# ============================================================================
# MONGODB (Documents & Images)
# ============================================================================

class MongoDB:
    """MongoDB connection manager"""

    def __init__(self):
        self.client: AsyncIOMotorClient | None = None
        self.db = None

    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(settings.mongodb_url)
            self.db = self.client[settings.mongodb_db]
            # Test connection
            await self.client.admin.command('ping')
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {str(e)}")
            raise

    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

    def get_collection(self, name: str):
        """Get MongoDB collection"""
        return self.db[name]


# Global MongoDB instance
mongodb = MongoDB()


# ============================================================================
# REDIS (Cache & Sessions)
# ============================================================================

class RedisCache:
    """Redis connection manager"""

    def __init__(self):
        self.redis: aioredis.Redis | None = None

    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis = await aioredis.from_url(
                f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}",
                password=settings.redis_password,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self.redis.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Redis connection failed: {str(e)}")
            raise

    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")

    async def get(self, key: str) -> str | None:
        """Get value from cache"""
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ttl: int | None = None):
        """Set value in cache with optional TTL"""
        if ttl:
            await self.redis.setex(key, ttl, value)
        else:
            await self.redis.set(key, value)

    async def delete(self, key: str):
        """Delete key from cache"""
        await self.redis.delete(key)


# Global Redis instance
redis_cache = RedisCache()


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

async def init_databases():
    """Initialize all database connections"""
    logger.info("Initializing database connections...")

    # PostgreSQL (handled by SQLAlchemy engine)
    logger.info("PostgreSQL engine created")

    # MongoDB
    await mongodb.connect()

    # Redis
    await redis_cache.connect()

    logger.info("All databases initialized successfully")


async def close_databases():
    """Close all database connections"""
    logger.info("Closing database connections...")

    # PostgreSQL
    await async_engine.dispose()
    logger.info("PostgreSQL connection closed")

    # MongoDB
    await mongodb.close()

    # Redis
    await redis_cache.close()

    logger.info("All databases closed successfully")
