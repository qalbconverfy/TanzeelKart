import redis.asyncio as aioredis
from redis.asyncio import Redis
from app.core.config import settings
import logging
import json

logger = logging.getLogger(__name__)

# ─── Singleton client ──────────────────────────────────────────────────────────
redis_client: Redis = None


async def init_redis() -> None:
    """Called on app startup — creates Redis connection pool."""
    global redis_client
    try:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30,
        )
        await redis_client.ping()
        logger.info("✅ Redis connected successfully")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        raise


async def close_redis() -> None:
    """Called on app shutdown."""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")


def get_redis() -> Redis:
    """FastAPI dependency — returns the shared Redis client."""
    return redis_client


# ─── OTP helpers ───────────────────────────────────────────────────────────────

OTP_KEY_PREFIX = "otp:"
OTP_ATTEMPTS_PREFIX = "otp_attempts:"
RESEND_COOLDOWN_PREFIX = "otp_resend:"
SESSION_PREFIX = "session:"
BLACKLIST_PREFIX = "blacklist:"


async def store_otp(phone: str, otp: str) -> None:
    """Store OTP in Redis with 10-minute expiry. Overwrites previous OTP."""
    key = f"{OTP_KEY_PREFIX}{phone}"
    await redis_client.setex(key, settings.OTP_EXPIRE_SECONDS, otp)

    # Reset attempt counter on fresh OTP
    attempts_key = f"{OTP_ATTEMPTS_PREFIX}{phone}"
    await redis_client.delete(attempts_key)

    # Set resend cooldown (30 seconds)
    cooldown_key = f"{RESEND_COOLDOWN_PREFIX}{phone}"
    await redis_client.setex(cooldown_key, settings.OTP_RESEND_SECONDS, "1")


async def verify_otp(phone: str, otp: str) -> bool:
    """
    Verify OTP — returns True if valid.
    Deletes OTP on success (one-time use).
    Increments attempt counter on failure.
    """
    key = f"{OTP_KEY_PREFIX}{phone}"
    stored = await redis_client.get(key)

    if not stored:
        return False  # expired or never sent

    attempts_key = f"{OTP_ATTEMPTS_PREFIX}{phone}"

    if stored == otp:
        # Correct — delete OTP immediately (one-time use)
        await redis_client.delete(key)
        await redis_client.delete(attempts_key)
        return True
    else:
        # Wrong — increment attempts
        await redis_client.incr(attempts_key)
        await redis_client.expire(attempts_key, settings.OTP_EXPIRE_SECONDS)
        return False


async def get_otp_attempts(phone: str) -> int:
    """Returns number of failed OTP attempts for a phone number."""
    key = f"{OTP_ATTEMPTS_PREFIX}{phone}"
    val = await redis_client.get(key)
    return int(val) if val else 0


async def can_resend_otp(phone: str) -> bool:
    """Returns True if resend cooldown has passed."""
    key = f"{RESEND_COOLDOWN_PREFIX}{phone}"
    return not await redis_client.exists(key)


async def get_resend_ttl(phone: str) -> int:
    """Returns seconds remaining in resend cooldown."""
    key = f"{RESEND_COOLDOWN_PREFIX}{phone}"
    ttl = await redis_client.ttl(key)
    return max(ttl, 0)


# ─── Session / Blacklist helpers ───────────────────────────────────────────────

async def store_session(user_id: str, data: dict, expire_seconds: int) -> None:
    """Store user session data (e.g. refresh token metadata)."""
    key = f"{SESSION_PREFIX}{user_id}"
    await redis_client.setex(key, expire_seconds, json.dumps(data))


async def get_session(user_id: str) -> dict | None:
    """Retrieve session data for a user."""
    key = f"{SESSION_PREFIX}{user_id}"
    val = await redis_client.get(key)
    return json.loads(val) if val else None


async def delete_session(user_id: str) -> None:
    """Delete session on logout."""
    key = f"{SESSION_PREFIX}{user_id}"
    await redis_client.delete(key)


async def blacklist_token(jti: str, expire_seconds: int) -> None:
    """Blacklist a JWT (e.g. on logout or password change)."""
    key = f"{BLACKLIST_PREFIX}{jti}"
    await redis_client.setex(key, expire_seconds, "1")


async def is_token_blacklisted(jti: str) -> bool:
    """Returns True if the given JWT ID is blacklisted."""
    key = f"{BLACKLIST_PREFIX}{jti}"
    return bool(await redis_client.exists(key))
