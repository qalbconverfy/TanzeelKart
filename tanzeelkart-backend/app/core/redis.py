import redis.asyncio as aioredis
from app.core.config import settings
from loguru import logger
from typing import Optional
import json


redis_client: Optional[aioredis.Redis] = None


async def init_redis() -> aioredis.Redis:
    global redis_client
    redis_client = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        max_connections=20,
    )
    logger.info("✅ Redis connected successfully")
    return redis_client


async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")


async def get_redis() -> aioredis.Redis:
    return redis_client


async def set_cache(key: str, value: dict, expire: int = 300):
    await redis_client.setex(key, expire, json.dumps(value))


async def get_cache(key: str) -> Optional[dict]:
    data = await redis_client.get(key)
    return json.loads(data) if data else None


async def delete_cache(key: str):
    await redis_client.delete(key)


async def set_otp(phone: str, otp: str, expire: int = 600):
    key = f"otp:{phone}"
    # String ke roop mein save karo
    await redis_client.setex(key, expire, str(otp))
    logger.info(f"✅ OTP saved: {key} = {otp}")


async def get_otp(phone: str) -> Optional[str]:
    key = f"otp:{phone}"
    value = await redis_client.get(key)
    logger.info(f"🔍 OTP fetched: {key} = {value}")
    # String return karo
    return str(value).strip() if value else None


async def delete_otp(phone: str):
    key = f"otp:{phone}"
    await redis_client.delete(key)
    logger.info(f"🗑️ OTP deleted: {key}")
