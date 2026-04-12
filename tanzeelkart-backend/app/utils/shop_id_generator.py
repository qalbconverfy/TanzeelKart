from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.shop_id import ShopIDCounter
from datetime import datetime


async def generate_shop_id(db: AsyncSession) -> str:
    year = datetime.now().year

    result = await db.execute(
        select(ShopIDCounter).where(
            ShopIDCounter.year == year
        )
    )
    counter = result.scalar_one_or_none()

    if not counter:
        counter = ShopIDCounter(year=year, counter=1)
        db.add(counter)
    else:
        counter.counter += 1

    await db.commit()

    shop_id = f"TK-{year}-{str(counter.counter).zfill(5)}"
    return shop_id
