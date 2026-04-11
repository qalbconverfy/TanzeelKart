from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole
from app.core.exceptions import AuthException, PermissionException

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_token(token)

    if not payload or payload.get("type") != "access":
        raise AuthException("Invalid or expired token")

    user_id = payload.get("sub")
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.is_deleted == False
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise AuthException("User not found")

    if not user.is_active:
        raise AuthException("Account is disabled")

    return user


async def get_current_shopkeeper(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.SHOPKEEPER:
        raise PermissionException("Shopkeeper access required")
    return current_user


async def get_current_delivery_boy(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.DELIVERY_BOY:
        raise PermissionException("Delivery boy access required")
    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise PermissionException("Admin access required")
    return current_user
    