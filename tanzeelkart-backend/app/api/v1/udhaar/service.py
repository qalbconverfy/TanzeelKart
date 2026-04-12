from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.udhaar import (
    Udhaar, UdhaarStatus,
    DeliveryChargeAccount
)
from app.models.user import User
from app.models.shop import Shop
from app.models.notification import Notification, NotificationType
from app.api.v1.udhaar.schemas import (
    AddUdhaarRequest,
    PayUdhaarRequest,
    UdhaarResponse,
    UdhaarSummaryResponse,
    DeliveryChargeResponse,
    PayDeliveryChargeRequest
)
from app.core.exceptions import (
    NotFoundException,
    ValidationException,
    PermissionException
)
from loguru import logger
from datetime import datetime, timedelta
import uuid


# ─────────────────────────────────────────
# Add Udhaar (Manual — Shop se)
# ─────────────────────────────────────────

async def add_udhaar(
    payload: AddUdhaarRequest,
    db: AsyncSession,
    current_user: User,
) -> dict:
    # Shop check
    shop_result = await db.execute(
        select(Shop).where(
            Shop.id == payload.shop_id,
            Shop.is_deleted == False
        )
    )
    shop = shop_result.scalar_one_or_none()
    if not shop:
        raise NotFoundException("Shop not found")

    due_date = datetime.utcnow() + timedelta(
        days=payload.due_days
    )

    udhaar = Udhaar(
        id=uuid.uuid4(),
        user_id=current_user.id,
        shop_id=shop.id,
        total_amount=payload.amount,
        amount_paid=0.0,
        amount_remaining=payload.amount,
        status=UdhaarStatus.PENDING,
        due_date=due_date,
        is_sunday_collection=True,
    )
    db.add(udhaar)

    # User pending update
    current_user.total_udhaar_pending += payload.amount

    # Notification
    notification = Notification(
        id=uuid.uuid4(),
        user_id=current_user.id,
        title="Udhaar Added 📒",
        body=(
            f"₹{payload.amount} ka udhaar add hua — "
            f"{shop.name}. "
            f"Due: {due_date.strftime('%d %b %Y')}"
        ),
        type=NotificationType.UDHAAR,
        data={
            "amount": payload.amount,
            "shop": shop.name,
            "due_date": str(due_date)
        }
    )
    db.add(notification)

    # Shopkeeper notification
    shop_notification = Notification(
        id=uuid.uuid4(),
        user_id=shop.owner_id,
        title="Naya Udhaar 📒",
        body=(
            f"{current_user.full_name} ne "
            f"₹{payload.amount} ka udhaar liya"
        ),
        type=NotificationType.UDHAAR,
        data={
            "amount": payload.amount,
            "user": current_user.full_name
        }
    )
    db.add(shop_notification)

    await db.commit()
    await db.refresh(udhaar)

    logger.info(
        f"Udhaar added: ₹{payload.amount} "
        f"— {current_user.phone}"
    )

    return {
        "success": True,
        "message": "Udhaar add ho gaya!",
        "udhaar_id": str(udhaar.id),
        "amount": payload.amount,
        "due_date": str(due_date)
    }


# ─────────────────────────────────────────
# Pay Udhaar
# ─────────────────────────────────────────

async def pay_udhaar(
    payload: PayUdhaarRequest,
    db: AsyncSession,
    current_user: User,
) -> dict:
    result = await db.execute(
        select(Udhaar).where(
            Udhaar.id == payload.udhaar_id,
            Udhaar.user_id == current_user.id,
            Udhaar.is_deleted == False
        )
    )
    udhaar = result.scalar_one_or_none()
    if not udhaar:
        raise NotFoundException("Udhaar not found")

    if udhaar.status == UdhaarStatus.COLLECTED:
        raise ValidationException("Udhaar already paid")

    if payload.amount > udhaar.amount_remaining:
        raise ValidationException(
            f"Amount exceeds remaining: "
            f"₹{udhaar.amount_remaining}"
        )

    udhaar.amount_paid += payload.amount
    udhaar.amount_remaining -= payload.amount
    current_user.total_udhaar_pending -= payload.amount

    if udhaar.amount_remaining <= 0:
        udhaar.status = UdhaarStatus.COLLECTED
        message = "Udhaar poora pay ho gaya! ✅"
    else:
        udhaar.status = UdhaarStatus.PARTIAL
        message = (
            f"Partial payment done. "
            f"₹{udhaar.amount_remaining} baaki hai"
        )

    # Notification
    notification = Notification(
        id=uuid.uuid4(),
        user_id=current_user.id,
        title="Udhaar Payment ✅",
        body=message,
        type=NotificationType.PAYMENT,
        data={
            "amount_paid": payload.amount,
            "remaining": udhaar.amount_remaining
        }
    )
    db.add(notification)
    await db.commit()

    logger.info(
        f"Udhaar paid: ₹{payload.amount} "
        f"— {current_user.phone}"
    )

    return {
        "success": True,
        "message": message,
        "amount_paid": payload.amount,
        "amount_remaining": udhaar.amount_remaining
    }


# ─────────────────────────────────────────
# Get My Udhaar Summary
# ─────────────────────────────────────────

async def get_my_udhaar(
    db: AsyncSession,
    current_user: User,
) -> UdhaarSummaryResponse:
    result = await db.execute(
        select(Udhaar).where(
            Udhaar.user_id == current_user.id,
            Udhaar.is_deleted == False
        ).order_by(Udhaar.created_at.desc())
    )
    udhaars = result.scalars().all()

    # Overdue check
    now = datetime.utcnow()
    total_overdue = 0.0
    for u in udhaars:
        if (
            u.due_date and
            u.due_date < now and
            u.status not in [
                UdhaarStatus.COLLECTED,
                UdhaarStatus.PAID
            ]
        ):
            u.is_overdue = True
            total_overdue += u.amount_remaining

    await db.commit()

    total_remaining = sum(
        u.amount_remaining for u in udhaars
        if u.status not in [
            UdhaarStatus.COLLECTED,
            UdhaarStatus.PAID
        ]
    )

    return UdhaarSummaryResponse(
        total_udhaar=sum(u.total_amount for u in udhaars),
        total_paid=sum(u.amount_paid for u in udhaars),
        total_remaining=total_remaining,
        overdue_amount=total_overdue,
        udhaar_list=[
            UdhaarResponse.model_validate(u)
            for u in udhaars
        ]
    )


# ─────────────────────────────────────────
# Get Delivery Charge Account
# ─────────────────────────────────────────

async def get_delivery_charge_account(
    db: AsyncSession,
    current_user: User,
) -> DeliveryChargeResponse:
    result = await db.execute(
        select(DeliveryChargeAccount).where(
            DeliveryChargeAccount.user_id == current_user.id
        )
    )
    account = result.scalar_one_or_none()

    if not account:
        return DeliveryChargeResponse(
            total_accumulated=0.0,
            total_paid=0.0,
            pending_amount=0.0,
            discount_percentage=0.0,
            is_sunday_pending=False,
            last_sunday_collected=None
        )

    return DeliveryChargeResponse.model_validate(account)


# ─────────────────────────────────────────
# Pay Delivery Charge
# ─────────────────────────────────────────

async def pay_delivery_charge(
    payload: PayDeliveryChargeRequest,
    db: AsyncSession,
    current_user: User,
) -> dict:
    result = await db.execute(
        select(DeliveryChargeAccount).where(
            DeliveryChargeAccount.user_id == current_user.id
        )
    )
    account = result.scalar_one_or_none()

    if not account or account.pending_amount <= 0:
        raise ValidationException(
            "No pending delivery charges"
        )

    if payload.amount > account.pending_amount:
        raise ValidationException(
            f"Amount exceeds pending: "
            f"₹{account.pending_amount}"
        )

    account.pending_amount -= payload.amount
    account.total_paid += payload.amount
    current_user.total_delivery_charges_pending -= payload.amount

    if account.pending_amount <= 0:
        account.is_sunday_pending = False
        message = "Saare delivery charges pay ho gaye! ✅"
    else:
        message = (
            f"₹{payload.amount} paid. "
            f"₹{account.pending_amount} baaki hai"
        )

    # Notification
    notification = Notification(
        id=uuid.uuid4(),
        user_id=current_user.id,
        title="Delivery Charge Paid ✅",
        body=message,
        type=NotificationType.PAYMENT,
        data={
            "amount_paid": payload.amount,
            "remaining": account.pending_amount
        }
    )
    db.add(notification)
    await db.commit()

    return {
        "success": True,
        "message": message,
        "amount_paid": payload.amount,
        "remaining": account.pending_amount
    }


# ─────────────────────────────────────────
# Shop Ka Udhaar List (Shopkeeper)
# ─────────────────────────────────────────

async def get_shop_udhaar_list(
    db: AsyncSession,
    current_user: User,
) -> list:
    shop_result = await db.execute(
        select(Shop).where(
            Shop.owner_id == current_user.id,
            Shop.is_deleted == False
        )
    )
    shop = shop_result.scalar_one_or_none()
    if not shop:
        raise NotFoundException("Shop not found")

    result = await db.execute(
        select(Udhaar).where(
            Udhaar.shop_id == shop.id,
            Udhaar.is_deleted == False,
            Udhaar.status.in_([
                UdhaarStatus.PENDING,
                UdhaarStatus.PARTIAL,
                UdhaarStatus.OVERDUE
            ])
        ).order_by(Udhaar.created_at.desc())
    )
    udhaars = result.scalars().all()

    udhaar_list = []
    for u in udhaars:
        user_result = await db.execute(
            select(User).where(User.id == u.user_id)
        )
        user = user_result.scalar_one_or_none()
        udhaar_dict = UdhaarResponse.model_validate(u).model_dump()
        udhaar_dict["user_name"] = user.full_name if user else ""
        udhaar_dict["user_phone"] = user.phone if user else ""
        udhaar_list.append(udhaar_dict)

    return udhaar_list
