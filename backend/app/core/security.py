from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import secrets
import string
import uuid

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# ─── Password Hashing ──────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ─── OTP Generation ────────────────────────────────────────────────────────────
def generate_otp() -> str:
    """Generate a cryptographically secure 6-digit OTP."""
    digits = string.digits
    return "".join(secrets.choice(digits) for _ in range(settings.OTP_LENGTH))


# ─── JWT Tokens ────────────────────────────────────────────────────────────────
def _create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    extra_claims: Optional[dict] = None,
) -> Tuple[str, str]:
    """
    Internal helper — creates a signed JWT.
    Returns (token_string, jti) where jti is the unique token ID.
    """
    jti = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    payload = {
        "sub": subject,           # user_id as string
        "type": token_type,       # "access" | "refresh"
        "jti": jti,               # unique token ID (for blacklisting)
        "iat": now,
        "exp": now + expires_delta,
    }

    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, jti


def create_access_token(
    user_id: str,
    role: str,
    extra_claims: Optional[dict] = None,
) -> Tuple[str, str]:
    """
    Create a short-lived access token.
    Returns (access_token, jti).
    """
    claims = {"role": role}
    if extra_claims:
        claims.update(extra_claims)

    return _create_token(
        subject=user_id,
        token_type="access",
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        extra_claims=claims,
    )


def create_refresh_token(user_id: str) -> Tuple[str, str]:
    """
    Create a long-lived refresh token.
    Returns (refresh_token, jti).
    """
    return _create_token(
        subject=user_id,
        token_type="refresh",
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT.
    Raises JWTError if invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError:
        raise


def create_token_pair(user_id: str, role: str) -> dict:
    """
    Convenience — creates both access and refresh tokens.
    Returns a dict ready to send in the API response.
    """
    access_token, access_jti = create_access_token(user_id=user_id, role=role)
    refresh_token, refresh_jti = create_refresh_token(user_id=user_id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # seconds
        "access_jti": access_jti,
        "refresh_jti": refresh_jti,
    }
