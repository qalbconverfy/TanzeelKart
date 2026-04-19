from typing import Optional
from loguru import logger
import redis.asyncio as aioredis
import json
from app.core.config import settings

_redis: Optional[aioredis.Redis] = None


async def init_redis() -> None:
    global _redis
    _redis = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        max_connections=20,
        socket_keepalive=True,
        socket_timeout=5,
        retry_on_timeout=True,
    )
    await _redis.ping()
    logger.info("✅ Redis connected")


async def close_redis() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        logger.info("Redis closed")


def get_redis() -> aioredis.Redis:
    if _redis is None:
        raise RuntimeError("Redis not initialized")
    return _redis


# ── OTP ──────────────────────────────────
async def set_otp(phone: str, otp: str) -> None:
    r = get_redis()
    await r.setex(
        f"otp:{phone}",
        settings.OTP_EXPIRE_SECONDS,
        str(otp)
    )


async def get_otp(phone: str) -> Optional[str]:
    r = get_redis()
    val = await r.get(f"otp:{phone}")
    return str(val).strip() if val else None


async def delete_otp(phone: str) -> None:
    r = get_redis()
    await r.delete(f"otp:{phone}")


# ── Generic ───────────────────────────────
async def set_key(
    key: str, value: str, expire: int
) -> None:
    r = get_redis()
    await r.setex(key, expire, value)


async def get_key(key: str) -> Optional[str]:
    r = get_redis()
    return await r.get(key)


async def delete_key(key: str) -> None:
    r = get_redis()
    await r.delete(key)


# ── Cache ─────────────────────────────────
async def set_cache(
    key: str, value: dict, expire: int = 300
) -> None:
    r = get_redis()
    await r.setex(key, expire, json.dumps(value))


async def get_cache(key: str) -> Optional[dict]:
    r = get_redis()
    data = await r.get(key)
    return json.loads(data) if data else None
