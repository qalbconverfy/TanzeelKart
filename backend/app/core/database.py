from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# ─── Engine ────────────────────────────────────────────────────────────────────
# NullPool is used for serverless/Render deployments to avoid stale connections
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_pre_ping=True,           # validates connection before use
    pool_recycle=1800,            # recycle connections every 30 min
)

# ─── Session Factory ───────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,       # avoid lazy-load errors after commit
    autocommit=False,
    autoflush=False,
)


# ─── Dependency ────────────────────────────────────────────────────────────────
async def get_db() -> AsyncSession:
    """FastAPI dependency — yields an async DB session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ─── Lifecycle helpers ─────────────────────────────────────────────────────────
async def init_db() -> None:
    """Called on app startup — verifies DB connection."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(lambda c: None)   # simple ping
        logger.info("✅ Database connected successfully")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise


async def close_db() -> None:
    """Called on app shutdown — disposes connection pool."""
    await engine.dispose()
    logger.info("Database connection pool closed")
