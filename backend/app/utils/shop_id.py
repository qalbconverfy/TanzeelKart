from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime
from app.core.database import Base
from sqlalchemy import Column, Integer, String
from app.models.base import BaseModel


class ShopIDCounter(BaseModel):
    __tablename__ = "shop_id_counters"
    year = Column(Integer, nullable=False)
    counter = Column(Integer, default=0)
    prefix = Column(String(10), default="TK")


async def generate_shop_code(
    db: AsyncSession,
) -> str:
    year = datetime.now().year
    result = await db.execute(
        select(ShopIDCounter).where(
            ShopIDCounter.year == year
        )
    )
    counter = result.scalar_one_or_none()

    if not counter:
        counter = ShopIDCounter(
            year=year, counter=1
        )
        db.add(counter)
    else:
        counter.counter += 1

    await db.flush()
    return f"TK-{year}-{str(counter.counter).zfill(5)}"
