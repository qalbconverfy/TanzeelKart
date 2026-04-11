from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.redis import get_redis
from app.api.v1.auth import schemas, service
from app.core.exceptions import AuthException
import redis.asyncio as aioredis

router = APIRouter()


@router.post("/send-otp", response_model=schemas.OTPResponse)
async def send_otp(
    payload: schemas.SendOTPRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    return await service.send_otp(payload, db, redis, background_tasks)


@router.post("/verify-otp", response_model=schemas.TokenResponse)
async def verify_otp(
    payload: schemas.VerifyOTPRequest,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    return await service.verify_otp(payload, db, redis)


@router.post("/refresh-token", response_model=schemas.TokenResponse)
async def refresh_token(
    payload: schemas.RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    return await service.refresh_token(payload, db)


@router.post("/logout")
async def logout(
    payload: schemas.LogoutRequest,
    redis: aioredis.Redis = Depends(get_redis),
):
    return await service.logout(payload, redis)