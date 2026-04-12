from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.user import User, UserRole
from app.models.shop import Shop, ShopStatus
from app.models.order import Order
from app.models.delivery import Delivery
from app.models.verification import (
    Verification, VerificationStatus, VerificationType
)
from app.models.admin import Admin
from app.models.notification import Notification, NotificationType
from app.api.v1.admin.schemas import (
    AddAdminRequest,
    VerifyShopRequest,
    VerifyMedicalRequest,
    AdminStatsResponse
)
from app.core.security import get_password_hash
from app.core.exceptions import (
    NotFoundException,
    PermissionException,
    DuplicateException
)
from loguru import logger
import uuid


# ─────────────────────────────────────────
# Platform Stats
# ─────────────────────────────────────────

async def get_platform_stats(
    db: AsyncSession,
) -> AdminStatsResponse:
    # Users
    users_count = await db.execute(
        select(func.count(User.id)).where(
            User.is_deleted == False
        )
    )

    # Shops
    shops_count = await db.execute(
        select(func.count(Shop.id)).where(
            Shop.is_deleted == False
        )
    )

    # Orders
    orders_count = await db.execute(
        select(func.count(Order.id)).where(
            Order.is_deleted == False
        )
    )

    # Deliveries
    deliveries_count = await db.execute(
        select(func.count(Delivery.id)).where(
            Delivery.is_deleted == False
        )
    )

    # Pending shop verifications
    pending_shops = await db.execute(
        select(func.count(Shop.id)).where(
            Shop.status == ShopStatus.PENDING
        )
    )

    # Pending medical verifications
    pending_medical = await db.execute(
        select(func.count(Verification.id)).where(
            Verification.type == VerificationType.MEDICAL,
            Verification.status == VerificationStatus.LAYER_5
        )
    )

    # Pending udhaar total
    udhaar_result = await db.execute(
        select(func.sum(User.total_udhaar_pending)).where(
            User.is_deleted == False
        )
    )

    # Pending delivery charges
    charge_result = await db.execute(
        select(
            func.sum(User.total_delivery_charges_pending)
        ).where(User.is_deleted == False)
    )

    return AdminStatsResponse(
        total_users=users_count.scalar() or 0,
        total_shops=shops_count.scalar() or 0,
        total_orders=orders_count.scalar() or 0,
        total_deliveries=deliveries_count.scalar() or 0,
        pending_shop_verifications=pending_shops.scalar() or 0,
        pending_medical_verifications=pending_medical.scalar() or 0,
        total_udhaar_pending=udhaar_result.scalar() or 0.0,
        total_delivery_charges_pending=charge_result.scalar() or 0.0,
    )


# ─────────────────────────────────────────
# Add Admin
# ─────────────────────────────────────────

async def add_admin(
    payload: AddAdminRequest,
    db: AsyncSession,
    current_admin: User,
) -> dict:
    # Current admin super admin hai?
    admin_result = await db.execute(
        select(Admin).where(
            Admin.user_id == current_admin.id
        )
    )
    admin = admin_result.scalar_one_or_none()
    if not admin or not admin.is_super_admin:
        raise PermissionException(
            "Only super admin can add admins"
        )

    # User dhundo
    user_result = await db.execute(
        select(User).where(
            User.phone == payload.user_phone
        )
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise NotFoundException("User not found")

    # Already admin hai?
    existing = await db.execute(
        select(Admin).where(Admin.user_id == user.id)
    )
    if existing.scalar_one_or_none():
        raise DuplicateException("User is already admin")

    # Admin banao
    new_admin = Admin(
        id=uuid.uuid4(),
        user_id=user.id,
        username=payload.username,
        hashed_password=get_password_hash(payload.password),
        is_super_admin=payload.is_super_admin,
        permissions=payload.permissions,
        added_by=current_admin.id,
        biometric_enabled=False,
    )
    db.add(new_admin)

    user.role = UserRole.ADMIN
    await db.commit()

    logger.info(
        f"Admin added: {payload.username} "
        f"by {current_admin.full_name}"
    )

    return {
        "success": True,
        "message": f"Admin {payload.username} added!",
        "username": payload.username
    }


# ─────────────────────────────────────────
# Verify Shop
# ─────────────────────────────────────────

async def verify_shop(
    payload: VerifyShopRequest,
    db: AsyncSession,
) -> dict:
    result = await db.execute(
        select(Shop).where(
            Shop.id == payload.shop_id,
            Shop.is_deleted == False
        )
    )
    shop = result.scalar_one_or_none()
    if not shop:
        raise NotFoundException("Shop not found")

    if payload.status == "verified":
        shop.status = ShopStatus.VERIFIED
        message = f"{shop.name} verified!"
        notif_body = (
            f"Aapki shop '{shop.name}' verify ho gayi! "
            f"Ab aap products add kar sakte hain."
        )
    else:
        shop.status = ShopStatus.SUSPENDED
        message = f"{shop.name} rejected"
        notif_body = (
            f"Aapki shop '{shop.name}' reject hui. "
            f"Reason: {payload.notes or 'N/A'}"
        )

    # Owner notification
    notification = Notification(
        id=uuid.uuid4(),
        user_id=shop.owner_id,
        title="Shop Verification Update",
        body=notif_body,
        type=NotificationType.SYSTEM,
        data={"shop_id": str(shop.id), "status": payload.status}
    )
    db.add(notification)
    await db.commit()

    logger.info(f"Shop {payload.status}: {shop.name}")
    return {"success": True, "message": message}


# ─────────────────────────────────────────
# Verify Medical
# ─────────────────────────────────────────

async def verify_medical(
    payload: VerifyMedicalRequest,
    db: AsyncSession,
) -> dict:
    result = await db.execute(
        select(Verification).where(
            Verification.user_id == payload.user_id,
            Verification.type == VerificationType.MEDICAL
        )
    )
    verification = result.scalar_one_or_none()
    if not verification:
        raise NotFoundException("Verification not found")

    if payload.status == "approved":
        verification.status = VerificationStatus.APPROVED
        verification.is_verified = True

        user_result = await db.execute(
            select(User).where(
                User.id == payload.user_id
            )
        )
        user = user_result.scalar_one_or_none()
        if user:
            user.is_verified = True
            user.verification_layer = 5

        message = "Medical verification approved!"
        notif_body = (
            "Aapki medical/pharmacy verification "
            "approved ho gayi! Ab aap shop add kar sakte hain."
        )
    else:
        verification.status = VerificationStatus.REJECTED
        verification.rejection_reason = payload.notes
        message = "Medical verification rejected"
        notif_body = (
            f"Medical verification reject hui. "
            f"Reason: {payload.notes or 'N/A'}"
        )

    notification = Notification(
        id=uuid.uuid4(),
        user_id=uuid.UUID(payload.user_id),
        title="Medical Verification Update",
        body=notif_body,
        type=NotificationType.SYSTEM,
        data={"status": payload.status}
    )
    db.add(notification)
    await db.commit()

    logger.info(f"Medical {payload.status}: {payload.user_id}")
    return {"success": True, "message": message}


# ─────────────────────────────────────────
# Pending Verifications List
# ─────────────────────────────────────────

async def get_pending_verifications(
    db: AsyncSession,
) -> dict:
    # Pending shops
    shops_result = await db.execute(
        select(Shop).where(
            Shop.status == ShopStatus.PENDING,
            Shop.is_deleted == False
        )
    )
    pending_shops = shops_result.scalars().all()

    # Pending medical
    medical_result = await db.execute(
        select(Verification).where(
            Verification.type == VerificationType.MEDICAL,
            Verification.status == VerificationStatus.LAYER_5
        )
    )
    pending_medical = medical_result.scalars().all()

    return {
        "pending_shops": [
            {
                "id": str(s.id),
                "name": s.name,
                "phone": s.phone,
                "category": s.category.value,
                "address": s.address,
                "created_at": str(s.created_at)
            }
            for s in pending_shops
        ],
        "pending_medical": [
            {
                "user_id": str(v.user_id),
                "license_number": v.license_number,
                "pharmacist_name": v.pharmacist_name,
                "registration_number": v.registration_number,
                "created_at": str(v.created_at)
            }
            for v in pending_medical
        ]
    }


# ─────────────────────────────────────────
# All Users List
# ─────────────────────────────────────────

async def get_all_users(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 50,
) -> list:
    offset = (page - 1) * per_page
    result = await db.execute(
        select(User).where(
            User.is_deleted == False
        ).order_by(
            User.created_at.desc()
        ).offset(offset).limit(per_page)
    )
    users = result.scalars().all()

    return [
        {
            "id": str(u.id),
            "full_name": u.full_name,
            "phone": u.phone,
            "role": u.role.value,
            "account_type": u.account_type.value if u.account_type else None,
            "is_verified": u.is_verified,
            "status": u.status.value,
            "village": u.village,
            "created_at": str(u.created_at)
        }
        for u in users
    ]
