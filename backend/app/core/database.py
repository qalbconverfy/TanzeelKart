from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from loguru import logger
from typing import AsyncGenerator
from app.core.config import settings


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    poolclass=NullPool,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"DB error: {e}")
            raise
        finally:
            await session.close()


async def init_db() -> None:
    try:
        # Import all models explicitly
        import app.models.user  # noqa
        import app.models.shop  # noqa
        import app.models.product  # noqa
        import app.models.order  # noqa
        import app.models.order_item  # noqa
        import app.models.delivery  # noqa
        import app.models.wallet  # noqa
        import app.models.udhaar  # noqa
        import app.models.notification  # noqa
        import app.models.verification  # noqa
        import app.models.admin  # noqa

        async with engine.begin() as conn:
            await conn.run_sync(
                Base.metadata.create_all
            )
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ DB init failed: {e}")
        raise
