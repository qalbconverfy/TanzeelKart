from typing import Optional
from loguru import logger
import redis.asyncio as aioredis
import json
from app.core.config import settings


# ── Global Client ─────────────────────────
_redis_client: Optional[aioredis.Redis] = None


async def init_redis() -> aioredis.Redis:
    global _redis_client
    _redis_client = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        max_connections=20,
        socket_keepalive=True,
        socket_timeout=5,
        retry_on_timeout=True,
    )
    # Test connection
    await _redis_client.ping()
    logger.info("✅ Redis connected")
    return _redis_client


async def close_redis() -> None:
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        logger.info("Redis closed")


async def get_redis() -> aioredis.Redis:
    if _redis_client is None:
        raise RuntimeError("Redis not initialized")
    return _redis_client


# ── OTP ──────────────────────────────────
async def set_otp(
    phone: str,
    otp: str,
    expire: int = None
) -> None:
    client = await get_redis()
    expire = expire or settings.OTP_EXPIRE_SECONDS
    key = f"otp:{phone}"
    await client.setex(key, expire, str(otp))
    logger.debug(f"OTP set for {phone}")


async def get_otp(phone: str) -> Optional[str]:
    client = await get_redis()
    key = f"otp:{phone}"
    value = await client.get(key)
    return str(value).strip() if value else None


async def delete_otp(phone: str) -> None:
    client = await get_redis()
    key = f"otp:{phone}"
    await client.delete(key)


# ── Cache ─────────────────────────────────
async def set_cache(
    key: str,
    value: dict,
    expire: int = 300
) -> None:
    client = await get_redis()
    await client.setex(key, expire, json.dumps(value))


async def get_cache(key: str) -> Optional[dict]:
    client = await get_redis()
    data = await client.get(key)
    return json.loads(data) if data else None


async def delete_cache(key: str) -> None:
    client = await get_redis()
    await client.delete(key)


# ── Generic Key-Value ─────────────────────
async def set_key(
    key: str,
    value: str,
    expire: int
) -> None:
    client = await get_redis()
    await client.setex(key, expire, value)


async def get_key(key: str) -> Optional[str]:
    client = await get_redis()
    return await client.get(key)


async def delete_key(key: str) -> None:
    client = await get_redis()
    await client.delete(key)
