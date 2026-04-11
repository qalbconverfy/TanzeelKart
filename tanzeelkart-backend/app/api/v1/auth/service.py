from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import BackgroundTasks
from app.models.user import User, UserRole, UserStatus
from app.core.security import (
    generate_otp,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.core.redis import set_otp, get_otp, delete_otp
from app.core.exceptions import AuthException, ValidationException
from app.api.v1.auth.schemas import (
    SendOTPRequest, VerifyOTPRequest,
    RefreshTokenRequest, LogoutRequest,
    OTPResponse, TokenResponse
)
from app.utils.sms import send_sms
from loguru import logger
import redis.asyncio as aioredis
import uuid


async def send_otp(
    payload: SendOTPRequest,
    db: AsyncSession,
    redis: aioredis.Redis,
    background_tasks: BackgroundTasks,
) -> OTPResponse:
    otp = generate_otp()
    await set_otp(payload.phone, otp)

    message = f"TanzeelKart OTP: {otp}. Valid for 10 minutes. - QalbConverfy"
    background_tasks.add_task(send_sms, payload.phone, message)

    logger.info(f"OTP sent to {payload.phone}")

    return OTPResponse(
        success=True,
        message="OTP sent successfully",
        phone=payload.phone
    )


async def verify_otp(
    payload: VerifyOTPRequest,
    db: AsyncSession,
    redis: aioredis.Redis,
) -> TokenResponse:
    stored_otp = await get_otp(payload.phone)

    if not stored_otp:
        raise AuthException("OTP expired or not found")

    if stored_otp != payload.otp:
        raise AuthException("Invalid OTP")

    await delete_otp(payload.phone)

    # Check existing user
    result = await db.execute(
        select(User).where(User.phone == payload.phone)
    )
    user = result.scalar_one_or_none()
    is_new_user = False

    if not user:
        # Create new user
        user = User(
            id=uuid.uuid4(),
            phone=payload.phone,
            full_name="",
            role=UserRole.BUYER,
            status=UserStatus.ACTIVE,
            is_phone_verified=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        is_new_user = True
        logger.info(f"New user created: {payload.phone}")

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    # Store refresh token in Redis
    await redis.setex(
        f"refresh:{str(user.id)}",
        60 * 60 * 24 * 7,
        refresh_token
    )

    return TokenResponse(
        success=True,
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=str(user.id),
        role=user.role.value,
        is_new_user=is_new_user
    )


async def refresh_token(
    payload: RefreshTokenRequest,
    db: AsyncSession,
) -> TokenResponse:
    token_data = decode_token(payload.refresh_token)

    if not token_data or token_data.get("type") != "refresh":
        raise AuthException("Invalid refresh token")

    user_id = token_data.get("sub")
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise AuthException("User not found")

    access_token = create_access_token(str(user.id))
    new_refresh_token = create_refresh_token(str(user.id))

    return TokenResponse(
        success=True,
        access_token=access_token,
        refresh_token=new_refresh_token,
        user_id=str(user.id),
        role=user.role.value,
    )


async def logout(
    payload: LogoutRequest,
    redis: aioredis.Redis,
) -> dict:
    token_data = decode_token(payload.refresh_token)
    if token_data:
        user_id = token_data.get("sub")
        await redis.delete(f"refresh:{user_id}")

    return {"success": True, "message": "Logged out successfully"}
    