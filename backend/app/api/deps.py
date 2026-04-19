from fastapi import Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import decode_token
from app.core.exceptions import (
    AuthException, ForbiddenException
)
from app.models.user import User, UserRole

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not credentials:
        raise AuthException("Token missing")

    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise AuthException("Invalid token")

    user_id = payload.get("sub")
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.is_deleted == False,
            User.is_active == True,
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        raise AuthException("User not found")

    return user


async def get_current_shopkeeper(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.SHOPKEEPER:
        raise ForbiddenException(
            "Shopkeeper access required"
        )
    return current_user


async def get_current_delivery_boy(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.DELIVERY_BOY:
        raise ForbiddenException(
            "Delivery boy access required"
        )
    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenException(
            "Admin access required"
        )
    return current_user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    if not credentials:
        return None
    try:
        return await get_current_user(
            credentials, db
        )
    except Exception:
        return None
