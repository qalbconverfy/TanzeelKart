from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.auth import (
    SendOTPRequest, VerifyOTPRequest,
    EmailRegisterRequest, EmailLoginRequest,
    SelectAccountTypeRequest,
    ShopVerifyLayer1, ShopVerifyLayer2,
    MedicalVerifyRequest,
    AdminLoginRequest, AdminOTPVerify,
    AdminBiometricVerify,
    RefreshTokenRequest, LogoutRequest,
    OTPResponse, TokenResponse,
)
from app.api.v1.auth import service

router = APIRouter()


# ── Phone OTP ─────────────────────────────
@router.post(
    "/send-otp",
    response_model=OTPResponse,
    summary="Phone OTP bhejo",
)
async def send_otp(
    payload: SendOTPRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    return await service.send_otp_service(
        payload, db, background_tasks
    )


@router.post(
    "/verify-otp",
    response_model=TokenResponse,
    summary="OTP verify karo",
)
async def verify_otp(
    payload: VerifyOTPRequest,
    db: AsyncSession = Depends(get_db),
):
    return await service.verify_otp_service(
        payload, db
    )


# ── Email ─────────────────────────────────
@router.post(
    "/email/register",
    response_model=TokenResponse,
    summary="Email se register",
)
async def email_register(
    payload: EmailRegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    return await service.email_register_service(
        payload, db, background_tasks
    )


@router.post(
    "/email/login",
    response_model=TokenResponse,
    summary="Email se login",
)
async def email_login(
    payload: EmailLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    return await service.email_login_service(
        payload, db
    )


# ── Guest ─────────────────────────────────
@router.post(
    "/guest",
    response_model=TokenResponse,
    summary="Guest login",
)
async def guest_login(
    db: AsyncSession = Depends(get_db),
):
    return await service.guest_login_service(db)


# ── Account Type ──────────────────────────
@router.post(
    "/account-type",
    summary="Account type select karo",
)
async def select_account_type(
    payload: SelectAccountTypeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.select_account_type_service(
        payload, db, current_user
    )


# ── Shop Verify ───────────────────────────
@router.post(
    "/verify/shop/layer-1",
    summary="Shop verify layer 1",
)
async def shop_verify_layer1(
    payload: ShopVerifyLayer1,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.shop_verify_layer1_service(
        payload, db, current_user
    )


@router.post(
    "/verify/shop/layer-2",
    summary="Shop verify layer 2",
)
async def shop_verify_layer2(
    payload: ShopVerifyLayer2,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.shop_verify_layer2_service(
        payload, db, current_user
    )


# ── Medical Verify ────────────────────────
@router.post(
    "/verify/medical",
    summary="Medical verify",
)
async def medical_verify(
    payload: MedicalVerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.medical_verify_service(
        payload, db, current_user
    )


# ── Admin ─────────────────────────────────
@router.post(
    "/admin/login",
    summary="Admin login layer 1",
)
async def admin_login(
    payload: AdminLoginRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    return await service.admin_login_layer1_service(
        payload, db, background_tasks
    )


@router.post(
    "/admin/verify-otp",
    summary="Admin OTP layer 2",
)
async def admin_verify_otp(
    payload: AdminOTPVerify,
    db: AsyncSession = Depends(get_db),
):
    return await service.admin_login_layer2_service(
        payload, db
    )


@router.post(
    "/admin/biometric",
    summary="Admin biometric layer 3",
)
async def admin_biometric(
    payload: AdminBiometricVerify,
    db: AsyncSession = Depends(get_db),
):
    return await service.admin_login_layer3_service(
        payload, db
    )


# ── Token ─────────────────────────────────
@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Token refresh karo",
)
async def refresh_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    return await service.refresh_token_service(
        payload, db
    )


@router.post(
    "/logout",
    summary="Logout",
)
async def logout(
    payload: LogoutRequest,
):
    return await service.logout_service(payload)
