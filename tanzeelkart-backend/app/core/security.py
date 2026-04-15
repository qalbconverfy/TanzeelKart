from datetime import datetime, timedelta, timezone
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
import secrets
import string


# ── Password ─────────────────────────────
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def verify_password(
    plain: str,
    hashed: str
) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# ── JWT ──────────────────────────────────
def create_access_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None,
    extra_data: Optional[dict] = None,
) -> str:
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta or
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "type": "access",
    }
    if extra_data:
        payload.update(extra_data)
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(
    subject: Union[str, int],
) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "type": "refresh",
    }
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        return None


# ── OTP ──────────────────────────────────
def generate_otp(length: int = 6) -> str:
    return "".join(
        secrets.choice(string.digits)
        for _ in range(length)
    )


# ── Random Keys ──────────────────────────
def generate_secret_key(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


def generate_short_id() -> str:
    return secrets.token_hex(4).upper()
