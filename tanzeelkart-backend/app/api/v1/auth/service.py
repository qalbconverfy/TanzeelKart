from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import BackgroundTasks
from app.models.user import User, UserRole, UserStatus, AccountType
from app.models.verification import (
    Verification, VerificationStatus, VerificationType
)
from app.models.admin import Admin
from app.core.security import (
    generate_otp,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
    get_password_hash
)
from app.core.redis import set_otp, get_otp, delete_otp
from app.core.exceptions import (
    AuthException, ValidationException,
    PermissionException, NotFoundException
)
from app.api.v1.auth import schemas
from app.utils.sms import send_sms
from app.utils.shop_id_generator import generate_shop_id
from loguru import logger
import redis.asyncio as aioredis
import uuid


# ─────────────────────────────────────────
# OTP
# ─────────────────────────────────────────

async def send_otp(
    payload: schemas.SendOTPRequest,
    db: AsyncSession,
    redis: aioredis.Redis,
    background_tasks: BackgroundTasks,
) -> schemas.OTPResponse:
    otp = generate_otp()
    await set_otp(payload.phone, otp)

    message = (
        f"TanzeelKart OTP: {otp}. "
        f"Valid 10 min. - QalbConverfy"
    )
    background_tasks.add_task(send_sms, payload.phone, message)
    logger.info(f"OTP sent to {payload.phone}")

    return schemas.OTPResponse(
        success=True,
        message="OTP sent successfully",
        phone=payload.phone
    )


async def verify_otp(
    payload: schemas.VerifyOTPRequest,
    db: AsyncSession,
    redis: aioredis.Redis,
) -> schemas.TokenResponse:
    stored_otp = await get_otp(payload.phone)

    if not stored_otp:
        raise AuthException("OTP expired or not found")
    if stored_otp != payload.otp:
        raise AuthException("Invalid OTP")

    await delete_otp(payload.phone)

    result = await db.execute(
        select(User).where(User.phone == payload.phone)
    )
    user = result.scalar_one_or_none()
    is_new_user = False

    if not user:
        user = User(
            id=uuid.uuid4(),
            phone=payload.phone,
            full_name="",
            role=UserRole.BUYER,
            status=UserStatus.ACTIVE,
            is_phone_verified=True,
            account_type=AccountType.SKIP,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        is_new_user = True
        logger.info(f"New user: {payload.phone}")

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    await redis.setex(
        f"refresh:{str(user.id)}",
        60 * 60 * 24 * 7,
        refresh_token
    )

    return schemas.TokenResponse(
        success=True,
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=str(user.id),
        role=user.role.value,
        account_type=user.account_type.value if user.account_type else None,
        is_new_user=is_new_user,
        is_verified=user.is_verified,
    )


# ─────────────────────────────────────────
# Account Type Select
# ─────────────────────────────────────────

async def select_account_type(
    payload: schemas.SelectAccountTypeRequest,
    db: AsyncSession,
) -> dict:
    result = await db.execute(
        select(User).where(User.id == payload.user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundException("User not found")

    user.account_type = AccountType(payload.account_type)

    # Role set karo
    if payload.account_type == "shop":
        user.role = UserRole.SHOPKEEPER
    elif payload.account_type == "medical":
        user.role = UserRole.SHOPKEEPER
    elif payload.account_type == "skip":
        user.role = UserRole.BUYER

    await db.commit()

    return {
        "success": True,
        "message": "Account type selected",
        "account_type": payload.account_type,
        "next_step": _get_next_step(payload.account_type)
    }


def _get_next_step(account_type: str) -> str:
    steps = {
        "shop": "complete_shop_verification",
        "medical": "complete_medical_verification",
        "normal": "complete",
        "all_types": "complete",
        "skip": "complete",
    }
    return steps.get(account_type, "complete")


# ─────────────────────────────────────────
# Shop Verification — 2 Layers
# ─────────────────────────────────────────

async def shop_verify_layer1(
    user_id: str,
    payload: schemas.ShopVerificationLayer1,
    db: AsyncSession,
) -> dict:
    result = await db.execute(
        select(Verification).where(
            Verification.user_id == user_id,
            Verification.type == VerificationType.SHOP
        )
    )
    verification = result.scalar_one_or_none()

    if not verification:
        verification = Verification(
            user_id=user_id,
            type=VerificationType.SHOP,
            total_layers=2,
            current_layer=1,
            shop_owner_name=payload.shop_owner_name,
            seller_name=payload.seller_name,
            status=VerificationStatus.LAYER_1,
        )
        db.add(verification)
    else:
        verification.shop_owner_name = payload.shop_owner_name
        verification.seller_name = payload.seller_name
        verification.current_layer = 1
        verification.status = VerificationStatus.LAYER_1

    await db.commit()
    return {
        "success": True,
        "message": "Layer 1 complete",
        "next_layer": 2
    }


async def shop_verify_layer2(
    user_id: str,
    payload: schemas.ShopVerificationLayer2,
    db: AsyncSession,
) -> dict:
    result = await db.execute(
        select(Verification).where(
            Verification.user_id == user_id,
            Verification.type == VerificationType.SHOP
        )
    )
    verification = result.scalar_one_or_none()

    if not verification or verification.current_layer < 1:
        raise ValidationException("Complete layer 1 first")

    # Shop ID verify karo
    shop_result = await db.execute(
        select(Verification).where(
            Verification.shop_id == payload.shop_id,
            Verification.is_verified == True
        )
    )
    existing = shop_result.scalar_one_or_none()
    if existing:
        raise ValidationException("Shop ID already registered")

    verification.shop_id = payload.shop_id
    verification.current_layer = 2
    verification.status = VerificationStatus.APPROVED
    verification.is_verified = True

    # User verified mark karo
    user_result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = user_result.scalar_one_or_none()
    if user:
        user.is_verified = True
        user.verification_layer = 2

    await db.commit()
    return {
        "success": True,
        "message": "Shop verification complete!",
        "shop_id": payload.shop_id
    }


# ─────────────────────────────────────────
# Medical Verification — 5 Layers
# ─────────────────────────────────────────

async def medical_verify_layer(
    user_id: str,
    layer: int,
    data: dict,
    db: AsyncSession,
) -> dict:
    result = await db.execute(
        select(Verification).where(
            Verification.user_id == user_id,
            Verification.type == VerificationType.MEDICAL
        )
    )
    verification = result.scalar_one_or_none()

    if not verification:
        verification = Verification(
            user_id=user_id,
            type=VerificationType.MEDICAL,
            total_layers=5,
            current_layer=0,
        )
        db.add(verification)
        await db.commit()
        await db.refresh(verification)

    if layer != verification.current_layer + 1:
        raise ValidationException(
            f"Complete layer {verification.current_layer} first"
        )

    # Har layer ka data save karo
    if layer == 1:
        verification.license_number = data.get("license_number")
        verification.status = VerificationStatus.LAYER_1
    elif layer == 2:
        verification.pharmacist_name = data.get("pharmacist_name")
        verification.status = VerificationStatus.LAYER_2
    elif layer == 3:
        verification.registration_number = data.get("registration_number")
        verification.status = VerificationStatus.LAYER_3
    elif layer == 4:
        verification.documents = data.get("documents")
        verification.status = VerificationStatus.LAYER_4
    elif layer == 5:
        # Layer 5 = Admin approval pending
        verification.status = VerificationStatus.LAYER_5

    verification.current_layer = layer

    # Layer 5 complete = Admin approval wait
    if layer == 5:
        await db.commit()
        return {
            "success": True,
            "message": "All layers complete! Waiting for admin approval.",
            "status": "pending_admin_approval"
        }

    await db.commit()
    return {
        "success": True,
        "message": f"Layer {layer} complete!",
        "next_layer": layer + 1
    }


# ─────────────────────────────────────────
# Admin Login — 3 Layers
# ─────────────────────────────────────────

async def admin_login_layer1(
    payload: schemas.AdminLoginRequest,
    db: AsyncSession,
    redis: aioredis.Redis,
    background_tasks: BackgroundTasks,
) -> dict:
    result = await db.execute(
        select(Admin).where(
            Admin.username == payload.username
        )
    )
    admin = result.scalar_one_or_none()

    if not admin:
        raise AuthException("Invalid credentials")
    if admin.is_locked:
        raise AuthException("Account locked. Contact support.")
    if not verify_password(payload.password, admin.hashed_password):
        raise AuthException("Invalid credentials")

    # Layer 1 passed — OTP bhejo
    user_result = await db.execute(
        select(User).where(User.id == admin.user_id)
    )
    user = user_result.scalar_one_or_none()

    if user and user.phone:
        otp = generate_otp()
        await redis.setex(f"admin_otp:{admin.username}", 600, otp)
        msg = f"TanzeelKart Admin OTP: {otp}. Valid 10 min."
        background_tasks.add_task(send_sms, user.phone, msg)

    return {
        "success": True,
        "message": "Layer 1 passed. OTP sent.",
        "next_layer": 2
    }


async def admin_login_layer2(
    payload: schemas.AdminOTPVerify,
    db: AsyncSession,
    redis: aioredis.Redis,
) -> dict:
    stored_otp = await redis.get(f"admin_otp:{payload.username}")
    if not stored_otp or stored_otp != payload.otp:
        raise AuthException("Invalid or expired OTP")

    await redis.delete(f"admin_otp:{payload.username}")

    result = await db.execute(
        select(Admin).where(Admin.username == payload.username)
    )
    admin = result.scalar_one_or_none()
    if not admin:
        raise AuthException("Admin not found")

    # Biometric enabled hai?
    if admin.biometric_enabled:
        await redis.setex(
            f"admin_biometric_pending:{payload.username}",
            300,
            "1"
        )
        return {
            "success": True,
            "message": "Layer 2 passed. Biometric required.",
            "next_layer": 3,
            "biometric_required": True
        }

    # Biometric nahi hai — directly token do
    return await _create_admin_token(admin, db)


async def admin_login_layer3_biometric(
    payload: schemas.AdminBiometricVerify,
    db: AsyncSession,
    redis: aioredis.Redis,
) -> dict:
    pending = await redis.get(
        f"admin_biometric_pending:{payload.username}"
    )
    if not pending:
        raise AuthException("Biometric session expired")

    result = await db.execute(
        select(Admin).where(Admin.username == payload.username)
    )
    admin = result.scalar_one_or_none()
    if not admin:
        raise AuthException("Admin not found")

    # Biometric verify karo
    if payload.biometric_token != admin.biometric_key:
        raise AuthException("Biometric verification failed")

    await redis.delete(f"admin_biometric_pending:{payload.username}")
    return await _create_admin_token(admin, db)


async def _create_admin_token(admin: Admin, db: AsyncSession) -> dict:
    from datetime import datetime
    admin.last_login = datetime.utcnow()
    await db.commit()

    access_token = create_access_token(str(admin.user_id))
    refresh_token = create_refresh_token(str(admin.user_id))

    return {
        "success": True,
        "message": "Admin login successful!",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "is_super_admin": admin.is_super_admin
    }


# ─────────────────────────────────────────
# Refresh + Logout
# ─────────────────────────────────────────

async def refresh_token(
    payload: schemas.RefreshTokenRequest,
    db: AsyncSession,
) -> schemas.TokenResponse:
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

    return schemas.TokenResponse(
        success=True,
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
        user_id=str(user.id),
        role=user.role.value,
        account_type=user.account_type.value if user.account_type else None,
        is_verified=user.is_verified,
    )


async def logout(
    payload: schemas.LogoutRequest,
    redis: aioredis.Redis,
) -> dict:
    token_data = decode_token(payload.refresh_token)
    if token_data:
        await redis.delete(f"refresh:{token_data.get('sub')}")
    return {"success": True, "message": "Logged out"}
