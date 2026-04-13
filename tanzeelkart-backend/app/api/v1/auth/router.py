from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.redis import get_redis
from app.api.v1.auth import schemas, service
import redis.asyncio as aioredis

router = APIRouter()


# ── OTP ──────────────────────────────────
@router.post("/send-otp", response_model=schemas.OTPResponse)
async def send_otp(
    payload: schemas.SendOTPRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    return await service.send_otp(
        payload, db, redis, background_tasks
    )


@router.post("/verify-otp", response_model=schemas.TokenResponse)
async def verify_otp(
    payload: schemas.VerifyOTPRequest,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    return await service.verify_otp(payload, db, redis)


# ── Account Type ─────────────────────────
@router.post("/select-account-type")
async def select_account_type(
    payload: schemas.SelectAccountTypeRequest,
    db: AsyncSession = Depends(get_db),
):
    return await service.select_account_type(payload, db)

# ── Email Register ────────────────────────
@router.post("/email/register")
async def email_register(
    payload: schemas.EmailRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    return await service.email_register(payload, db)


# ── Email Login ───────────────────────────
@router.post("/email/login")
async def email_login(
    payload: schemas.EmailLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    return await service.email_login(payload, db)


# ── Guest Login ───────────────────────────
@router.post("/guest/login")
async def guest_login(
    db: AsyncSession = Depends(get_db),
):
    return await service.guest_login(db)

# ── Shop Verification ────────────────────
@router.post("/shop-verify/layer-1")
async def shop_verify_layer1(
    user_id: str,
    payload: schemas.ShopVerificationLayer1,
    db: AsyncSession = Depends(get_db),
):
    return await service.shop_verify_layer1(user_id, payload, db)


@router.post("/shop-verify/layer-2")
async def shop_verify_layer2(
    user_id: str,
    payload: schemas.ShopVerificationLayer2,
    db: AsyncSession = Depends(get_db),
):
    return await service.shop_verify_layer2(user_id, payload, db)


# ── Medical Verification ─────────────────
@router.post("/medical-verify/layer-{layer}")
async def medical_verify(
    user_id: str,
    layer: int,
    data: dict,
    db: AsyncSession = Depends(get_db),
):
    return await service.medical_verify_layer(
        user_id, layer, data, db
    )


# ── Admin Login ───────────────────────────
@router.post("/admin/login")
async def admin_login(
    payload: schemas.AdminLoginRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    return await service.admin_login_layer1(
        payload, db, redis, background_tasks
    )


@router.post("/admin/verify-otp")
async def admin_verify_otp(
    payload: schemas.AdminOTPVerify,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    return await service.admin_login_layer2(payload, db, redis)


@router.post("/admin/biometric")
async def admin_biometric(
    payload: schemas.AdminBiometricVerify,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    return await service.admin_login_layer3_biometric(
        payload, db, redis
    )


# ── Token ────────────────────────────────
@router.post("/refresh-token")
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
