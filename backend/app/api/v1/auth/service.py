from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import BackgroundTasks
import uuid
from loguru import logger

from app.models.user import (
    User, UserRole, UserStatus,
    AccountType, LoginMethod,
)
from app.models.verification import (
    Verification, VerificationStatus,
    VerificationType,
)
from app.models.admin import Admin
from app.models.wallet import Wallet, WalletType
from app.core.security import (
    generate_otp, create_access_token,
    create_refresh_token, decode_token,
    verify_password, get_password_hash,
)
from app.core.redis import (
    set_otp, get_otp, delete_otp,
    set_key, get_key, delete_key,
)
from app.core.exceptions import (
    AuthException, ConflictException,
    NotFoundException, ValidationException,
    ForbiddenException,
)
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
from app.services.sms import send_sms
from app.services.email import send_otp_email
from app.utils.shop_id import generate_shop_code


# ─────────────────────────────────────────
# Helper
# ─────────────────────────────────────────

async def _create_wallet(
    db: AsyncSession,
    user_id: uuid.UUID,
    wallet_type: WalletType = WalletType.USER,
) -> Wallet:
    wallet = Wallet(
        user_id=user_id,
        wallet_type=wallet_type,
    )
    db.add(wallet)
    await db.flush()
    return wallet


def _create_tokens(user_id: str) -> dict:
    return {
        "access_token": create_access_token(user_id),
        "refresh_token": create_refresh_token(user_id),
    }


# ─────────────────────────────────────────
# Phone OTP
# ─────────────────────────────────────────

async def send_otp_service(
    payload: SendOTPRequest,
    db: AsyncSession,
    background_tasks: BackgroundTasks,
) -> OTPResponse:
    otp = generate_otp()
    await set_otp(payload.phone, otp)

    logger.info(f"🔑 OTP for {payload.phone}: {otp}")

    message = (
        f"TanzeelKart OTP: {otp}. "
        f"Valid 10 min. -QalbConverfy"
    )
    background_tasks.add_task(
        send_sms, payload.phone, message
    )

    return OTPResponse(
        success=True,
        message="OTP sent successfully",
        phone=payload.phone,
    )


async def verify_otp_service(
    payload: VerifyOTPRequest,
    db: AsyncSession,
) -> TokenResponse:
    phone = payload.phone
    entered = str(payload.otp).strip()

    stored = await get_otp(phone)
    logger.info(
        f"OTP check — stored: {stored}, entered: {entered}"
    )

    if not stored:
        raise AuthException(
            "OTP expire ho gaya — dobara bhejo"
        )
    if stored != entered:
        raise AuthException("OTP galat hai")

    await delete_otp(phone)

    # Get or create user
    result = await db.execute(
        select(User).where(User.phone == phone)
    )
    user = result.scalar_one_or_none()
    is_new = False

    if not user:
        user = User(
            phone=phone,
            full_name="",
            role=UserRole.BUYER,
            status=UserStatus.ACTIVE,
            login_method=LoginMethod.PHONE,
            is_phone_verified=True,
            account_type=AccountType.SKIP,
        )
        db.add(user)
        await db.flush()
        await _create_wallet(db, user.id)
        await db.commit()
        await db.refresh(user)
        is_new = True
        logger.info(f"✅ New user: {phone}")

    tokens = _create_tokens(str(user.id))

    # Store refresh token
    await set_key(
        f"refresh:{user.id}",
        tokens["refresh_token"],
        60 * 60 * 24 * 7,
    )

    return TokenResponse(
        success=True,
        **tokens,
        user_id=str(user.id),
        role=user.role.value,
        account_type=(
            user.account_type.value
            if user.account_type else None
        ),
        is_new_user=is_new,
        is_verified=user.is_verified,
    )


# ─────────────────────────────────────────
# Email Auth
# ─────────────────────────────────────────

async def email_register_service(
    payload: EmailRegisterRequest,
    db: AsyncSession,
    background_tasks: BackgroundTasks,
) -> TokenResponse:
    # Check existing
    result = await db.execute(
        select(User).where(User.email == payload.email)
    )
    if result.scalar_one_or_none():
        raise ConflictException(
            "Email already registered"
        )

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=get_password_hash(
            payload.password
        ),
        role=UserRole.BUYER,
        status=UserStatus.ACTIVE,
        login_method=LoginMethod.EMAIL,
        is_email_verified=False,
        account_type=AccountType.SKIP,
    )
    db.add(user)
    await db.flush()
    await _create_wallet(db, user.id)
    await db.commit()
    await db.refresh(user)

    # Send verification OTP
    otp = generate_otp()
    await set_otp(payload.email, otp)
    background_tasks.add_task(
        send_otp_email,
        payload.email,
        otp,
        payload.full_name,
    )

    tokens = _create_tokens(str(user.id))
    await set_key(
        f"refresh:{user.id}",
        tokens["refresh_token"],
        60 * 60 * 24 * 7,
    )

    logger.info(f"✅ Email register: {payload.email}")

    return TokenResponse(
        success=True,
        **tokens,
        user_id=str(user.id),
        role=user.role.value,
        account_type=AccountType.SKIP.value,
        is_new_user=True,
        is_verified=False,
    )


async def email_login_service(
    payload: EmailLoginRequest,
    db: AsyncSession,
) -> TokenResponse:
    result = await db.execute(
        select(User).where(User.email == payload.email)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise AuthException("Email registered nahi hai")
    if not user.hashed_password:
        raise AuthException(
            "Is account mein password nahi hai"
        )
    if not verify_password(
        payload.password, user.hashed_password
    ):
        raise AuthException("Password galat hai")
    if user.status == UserStatus.SUSPENDED:
        raise AuthException("Account suspended hai")

    tokens = _create_tokens(str(user.id))
    await set_key(
        f"refresh:{user.id}",
        tokens["refresh_token"],
        60 * 60 * 24 * 7,
    )

    logger.info(f"✅ Email login: {payload.email}")

    return TokenResponse(
        success=True,
        **tokens,
        user_id=str(user.id),
        role=user.role.value,
        account_type=(
            user.account_type.value
            if user.account_type else None
        ),
        is_verified=user.is_verified,
    )


# ─────────────────────────────────────────
# Guest Login
# ─────────────────────────────────────────

async def guest_login_service(
    db: AsyncSession,
) -> TokenResponse:
    user = User(
        full_name="Guest",
        role=UserRole.GUEST,
        status=UserStatus.ACTIVE,
        login_method=LoginMethod.GUEST,
        is_guest=True,
        account_type=AccountType.SKIP,
    )
    db.add(user)
    await db.flush()
    await db.commit()
    await db.refresh(user)

    tokens = _create_tokens(str(user.id))

    logger.info(f"✅ Guest: {user.id}")

    return TokenResponse(
        success=True,
        **tokens,
        user_id=str(user.id),
        role=user.role.value,
        is_guest=True,
    )


# ─────────────────────────────────────────
# Account Type
# ─────────────────────────────────────────

async def select_account_type_service(
    payload: SelectAccountTypeRequest,
    db: AsyncSession,
    current_user: User,
) -> dict:
    current_user.account_type = AccountType(
        payload.account_type
    )

    role_map = {
        "shop": UserRole.SHOPKEEPER,
        "medical": UserRole.SHOPKEEPER,
        "normal": UserRole.BUYER,
        "all_types": UserRole.BUYER,
        "skip": UserRole.BUYER,
    }
    current_user.role = role_map.get(
        payload.account_type, UserRole.BUYER
    )

    await db.commit()

    next_step_map = {
        "shop": "verify_shop",
        "medical": "verify_medical",
        "normal": "home",
        "all_types": "home",
        "skip": "home",
    }

    return {
        "success": True,
        "message": "Account type selected",
        "account_type": payload.account_type,
        "next_step": next_step_map.get(
            payload.account_type, "home"
        ),
    }


# ─────────────────────────────────────────
# Shop Verification
# ─────────────────────────────────────────

async def shop_verify_layer1_service(
    payload: ShopVerifyLayer1,
    db: AsyncSession,
    current_user: User,
) -> dict:
    result = await db.execute(
        select(Verification).where(
            Verification.user_id == current_user.id
        )
    )
    verification = result.scalar_one_or_none()

    if not verification:
        verification = Verification(
            user_id=current_user.id,
            type=VerificationType.SHOP,
            total_layers=2,
            current_layer=1,
            shop_owner_name=payload.shop_owner_name,
            seller_name=payload.seller_name,
            status=VerificationStatus.LAYER_1,
        )
        db.add(verification)
    else:
        verification.shop_owner_name = (
            payload.shop_owner_name
        )
        verification.seller_name = payload.seller_name
        verification.current_layer = 1
        verification.status = VerificationStatus.LAYER_1

    await db.commit()
    return {
        "success": True,
        "message": "Layer 1 complete!",
        "next_layer": 2,
    }


async def shop_verify_layer2_service(
    payload: ShopVerifyLayer2,
    db: AsyncSession,
    current_user: User,
) -> dict:
    result = await db.execute(
        select(Verification).where(
            Verification.user_id == current_user.id
        )
    )
    verification = result.scalar_one_or_none()

    if not verification or verification.current_layer < 1:
        raise ValidationException(
            "Layer 1 pehle complete karo"
        )

    # Check if shop code already used
    existing = await db.execute(
        select(Verification).where(
            Verification.shop_code == payload.shop_code,
            Verification.is_verified == True,
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictException(
            "Shop code already registered"
        )

    verification.shop_code = payload.shop_code
    verification.current_layer = 2
    verification.status = VerificationStatus.APPROVED
    verification.is_verified = True
    current_user.is_verified = True
    current_user.verification_layer = 2

    await db.commit()

    return {
        "success": True,
        "message": "Shop verification complete! 🎉",
        "shop_code": payload.shop_code,
    }


# ─────────────────────────────────────────
# Medical Verification (5 Layers)
# ─────────────────────────────────────────

async def medical_verify_service(
    payload: MedicalVerifyRequest,
    db: AsyncSession,
    current_user: User,
) -> dict:
    result = await db.execute(
        select(Verification).where(
            Verification.user_id == current_user.id
        )
    )
    verification = result.scalar_one_or_none()

    if not verification:
        if payload.layer != 1:
            raise ValidationException(
                "Layer 1 se shuru karo"
            )
        verification = Verification(
            user_id=current_user.id,
            type=VerificationType.MEDICAL,
            total_layers=5,
            current_layer=0,
        )
        db.add(verification)
        await db.flush()

    if payload.layer != verification.current_layer + 1:
        raise ValidationException(
            f"Layer {verification.current_layer + 1} chahiye"
        )

    layer_status = {
        1: VerificationStatus.LAYER_1,
        2: VerificationStatus.LAYER_2,
        3: VerificationStatus.LAYER_3,
        4: VerificationStatus.LAYER_4,
        5: VerificationStatus.LAYER_5,
    }

    if payload.layer == 1:
        verification.license_number = (
            payload.license_number
        )
    elif payload.layer == 2:
        verification.pharmacist_name = (
            payload.pharmacist_name
        )
    elif payload.layer == 3:
        verification.registration_number = (
            payload.registration_number
        )
    elif payload.layer == 4:
        verification.documents = {
            "url": payload.document_url
        }
    elif payload.layer == 5:
        pass  # Admin approval pending

    verification.current_layer = payload.layer
    verification.status = layer_status[payload.layer]
    current_user.verification_layer = payload.layer

    await db.commit()

    if payload.layer == 5:
        return {
            "success": True,
            "message": "Sab layers complete! Admin approval pending.",
            "status": "pending_admin_approval",
        }

    return {
        "success": True,
        "message": f"Layer {payload.layer} complete!",
        "next_layer": payload.layer + 1,
    }


# ─────────────────────────────────────────
# Admin Login (3 Layers)
# ─────────────────────────────────────────

async def admin_login_layer1_service(
    payload: AdminLoginRequest,
    db: AsyncSession,
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
        raise AuthException(
            "Account locked. Contact support."
        )
    if not verify_password(
        payload.password, admin.hashed_password
    ):
        admin.failed_attempts += 1
        if admin.failed_attempts >= 5:
            admin.is_locked = True
        await db.commit()
        raise AuthException("Invalid credentials")

    admin.failed_attempts = 0
    await db.commit()

    # Get user phone
    user_result = await db.execute(
        select(User).where(User.id == admin.user_id)
    )
    user = user_result.scalar_one_or_none()

    otp = generate_otp()
    await set_key(
        f"admin_otp:{admin.username}",
        otp, 600
    )

    if user and user.phone:
        msg = f"TanzeelKart Admin OTP: {otp}. Valid 10 min."
        background_tasks.add_task(
            send_sms, user.phone, msg
        )

    return {
        "success": True,
        "message": "Layer 1 passed. OTP sent.",
        "next_layer": 2,
    }


async def admin_login_layer2_service(
    payload: AdminOTPVerify,
    db: AsyncSession,
) -> dict:
    stored = await get_key(
        f"admin_otp:{payload.username}"
    )

    if not stored or str(stored).strip() != str(payload.otp).strip():
        raise AuthException("Invalid or expired OTP")

    await delete_key(f"admin_otp:{payload.username}")

    result = await db.execute(
        select(Admin).where(
            Admin.username == payload.username
        )
    )
    admin = result.scalar_one_or_none()
    if not admin:
        raise AuthException("Admin not found")

    if admin.biometric_enabled:
        await set_key(
            f"admin_bio:{payload.username}",
            "1", 300
        )
        return {
            "success": True,
            "message": "Layer 2 passed. Biometric required.",
            "next_layer": 3,
            "biometric_required": True,
        }

    return await _create_admin_token(admin, db)


async def admin_login_layer3_service(
    payload: AdminBiometricVerify,
    db: AsyncSession,
) -> dict:
    pending = await get_key(
        f"admin_bio:{payload.username}"
    )
    if not pending:
        raise AuthException("Biometric session expired")

    result = await db.execute(
        select(Admin).where(
            Admin.username == payload.username
        )
    )
    admin = result.scalar_one_or_none()
    if not admin:
        raise AuthException("Admin not found")

    if payload.biometric_token != admin.biometric_key:
        raise AuthException("Biometric failed")

    await delete_key(f"admin_bio:{payload.username}")
    return await _create_admin_token(admin, db)


async def _create_admin_token(
    admin: Admin,
    db: AsyncSession,
) -> dict:
    from datetime import datetime, timezone
    admin.last_login = datetime.now(timezone.utc)
    await db.commit()

    tokens = _create_tokens(str(admin.user_id))
    return {
        "success": True,
        "message": "Admin login successful!",
        **tokens,
        "token_type": "bearer",
        "is_super_admin": admin.is_super_admin,
    }


# ─────────────────────────────────────────
# Refresh + Logout
# ─────────────────────────────────────────

async def refresh_token_service(
    payload: RefreshTokenRequest,
    db: AsyncSession,
) -> TokenResponse:
    data = decode_token(payload.refresh_token)
    if not data or data.get("type") != "refresh":
        raise AuthException("Invalid refresh token")

    result = await db.execute(
        select(User).where(User.id == data["sub"])
    )
    user = result.scalar_one_or_none()
    if not user:
        raise AuthException("User not found")

    tokens = _create_tokens(str(user.id))
    await set_key(
        f"refresh:{user.id}",
        tokens["refresh_token"],
        60 * 60 * 24 * 7,
    )

    return TokenResponse(
        success=True,
        **tokens,
        user_id=str(user.id),
        role=user.role.value,
        account_type=(
            user.account_type.value
            if user.account_type else None
        ),
        is_verified=user.is_verified,
    )


async def logout_service(
    payload: LogoutRequest,
) -> dict:
    data = decode_token(payload.refresh_token)
    if data:
        await delete_key(f"refresh:{data.get('sub')}")
    return {"success": True, "message": "Logged out"}
