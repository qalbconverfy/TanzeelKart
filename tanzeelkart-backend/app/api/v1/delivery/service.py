
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.delivery import Delivery, DeliveryStatus
from app.models.order import Order, OrderStatus, PaymentStatus
from app.models.shop import Shop
from app.models.user import User, UserRole
from app.models.udhaar import (
    Udhaar, UdhaarStatus,
    DeliveryChargeAccount
)
from app.models.notification import Notification, NotificationType
from app.api.v1.delivery.schemas import (
    AssignDeliveryRequest,
    UpdateDeliveryStatusRequest,
    UpdateLocationRequest,
    CollectPaymentRequest,
    SundayCollectionRequest,
    DeliveryResponse
)
from app.core.exceptions import (
    NotFoundException,
    PermissionException,
    ValidationException
)
from loguru import logger
from datetime import datetime, timedelta
import uuid


# ─────────────────────────────────────────
# Create Delivery (Auto — Order Accept hone pe)
# ─────────────────────────────────────────

async def create_delivery_for_order(
    order: Order,
    shop: Shop,
    db: AsyncSession,
) -> Delivery:
    estimated_time = datetime.utcnow() + timedelta(hours=2)

    delivery = Delivery(
        id=uuid.uuid4(),
        order_id=order.id,
        shop_id=shop.id,
        buyer_id=order.buyer_id,
        status=DeliveryStatus.PENDING,
        pickup_latitude=shop.latitude,
        pickup_longitude=shop.longitude,
        delivery_latitude=order.delivery_latitude or 0.0,
        delivery_longitude=order.delivery_longitude or 0.0,
        delivery_address=order.delivery_address,
        delivery_charge=order.delivery_charge,
        is_charge_pending=order.delivery_charge_added_to_account,
        estimated_delivery_time=estimated_time,
    )
    db.add(delivery)
    await db.flush()
    logger.info(f"Delivery created for order: {order.id}")
    return delivery


# ─────────────────────────────────────────
# Assign Delivery Boy
# ─────────────────────────────────────────

async def assign_delivery(
    payload: AssignDeliveryRequest,
    db: AsyncSession,
    current_user: User,
) -> dict:
    # Delivery boy check
    if current_user.role != UserRole.DELIVERY_BOY:
        raise PermissionException(
            "Only delivery boys can accept deliveries"
        )

    result = await db.execute(
        select(Delivery).where(
            Delivery.order_id == payload.order_id,
            Delivery.is_deleted == False,
            Delivery.status == DeliveryStatus.PENDING
        )
    )
    delivery = result.scalar_one_or_none()
    if not delivery:
        raise NotFoundException(
            "Delivery not found or already assigned"
        )

    delivery.delivery_boy_id = current_user.id
    delivery.status = DeliveryStatus.ASSIGNED
    delivery.assigned_at = datetime.utcnow()

    # Buyer ko notification
    notification = Notification(
        id=uuid.uuid4(),
        user_id=delivery.buyer_id,
        title="Delivery Boy Assigned! 🛵",
        body=(
            f"Aapka delivery boy assign ho gaya. "
            f"1-2 ghante mein delivery hogi!"
        ),
        type=NotificationType.DELIVERY,
        data={
            "delivery_id": str(delivery.id),
            "delivery_boy": current_user.full_name
        }
    )
    db.add(notification)
    await db.commit()

    logger.info(
        f"Delivery assigned to: {current_user.full_name}"
    )

    return {
        "success": True,
        "message": "Delivery assigned successfully!",
        "delivery_id": str(delivery.id),
        "estimated_time": str(
            delivery.estimated_delivery_time
        )
    }


# ─────────────────────────────────────────
# Update Delivery Status
# ─────────────────────────────────────────

async def update_delivery_status(
    delivery_id: str,
    payload: UpdateDeliveryStatusRequest,
    db: AsyncSession,
    current_user: User,
) -> dict:
    result = await db.execute(
        select(Delivery).where(
            Delivery.id == delivery_id,
            Delivery.delivery_boy_id == current_user.id,
            Delivery.is_deleted == False
        )
    )
    delivery = result.scalar_one_or_none()
    if not delivery:
        raise NotFoundException("Delivery not found")

    # Location update
    if payload.current_latitude:
        delivery.current_latitude = payload.current_latitude
    if payload.current_longitude:
        delivery.current_longitude = payload.current_longitude

    old_status = delivery.status
    delivery.status = DeliveryStatus(payload.status)

    # Timestamps
    if payload.status == "picked":
        delivery.picked_at = datetime.utcnow()
    elif payload.status == "delivered":
        delivery.delivered_at = datetime.utcnow()
        await _handle_delivery_complete(delivery, db)

    # Buyer notification
    status_messages = {
        "picked": "Delivery boy shop se nikla! 🛵",
        "on_way": "Delivery boy raaste mein hai! 📍",
        "delivered": "Order deliver ho gaya! ✅",
        "failed": "Delivery failed. Contact karo."
    }

    notification = Notification(
        id=uuid.uuid4(),
        user_id=delivery.buyer_id,
        title="Delivery Update",
        body=status_messages.get(payload.status, ""),
        type=NotificationType.DELIVERY,
        data={
            "delivery_id": str(delivery.id),
            "status": payload.status
        }
    )
    db.add(notification)
    await db.commit()

    return {
        "success": True,
        "message": f"Status updated to {payload.status}",
        "delivery_id": delivery_id
    }


# ─────────────────────────────────────────
# Handle Delivery Complete
# ─────────────────────────────────────────

async def _handle_delivery_complete(
    delivery: Delivery,
    db: AsyncSession,
) -> None:
    # Order status update
    order_result = await db.execute(
        select(Order).where(Order.id == delivery.order_id)
    )
    order = order_result.scalar_one_or_none()
    if order:
        order.status = OrderStatus.DELIVERED
        if order.payment_method.value == "cash":
            order.payment_status = PaymentStatus.PAID
            order.amount_paid_offline = order.total_amount
            order.amount_remaining = 0.0

    logger.info(f"Delivery completed: {delivery.id}")


# ─────────────────────────────────────────
# Update Live Location
# ─────────────────────────────────────────

async def update_live_location(
    delivery_id: str,
    payload: UpdateLocationRequest,
    db: AsyncSession,
    current_user: User,
) -> dict:
    result = await db.execute(
        select(Delivery).where(
            Delivery.id == delivery_id,
            Delivery.delivery_boy_id == current_user.id,
            Delivery.is_deleted == False
        )
    )
    delivery = result.scalar_one_or_none()
    if not delivery:
        raise NotFoundException("Delivery not found")

    delivery.current_latitude = payload.latitude
    delivery.current_longitude = payload.longitude
    await db.commit()

    return {
        "success": True,
        "message": "Location updated",
        "latitude": payload.latitude,
        "longitude": payload.longitude
    }


# ─────────────────────────────────────────
# My Deliveries (Delivery Boy)
# ─────────────────────────────────────────

async def get_my_deliveries(
    db: AsyncSession,
    current_user: User,
    status: str = None,
    page: int = 1,
    per_page: int = 20,
) -> list:
    offset = (page - 1) * per_page
    query = select(Delivery).where(
        Delivery.delivery_boy_id == current_user.id,
        Delivery.is_deleted == False
    )

    if status:
        query = query.where(
            Delivery.status == DeliveryStatus(status)
        )

    result = await db.execute(
        query.order_by(
            Delivery.created_at.desc()
        ).offset(offset).limit(per_page)
    )
    deliveries = result.scalars().all()
    return [DeliveryResponse.model_validate(d) for d in deliveries]


# ─────────────────────────────────────────
# Pending Deliveries (Available for pickup)
# ─────────────────────────────────────────

async def get_pending_deliveries(
    db: AsyncSession,
    current_user: User,
) -> list:
    result = await db.execute(
        select(Delivery).where(
            Delivery.status == DeliveryStatus.PENDING,
            Delivery.is_deleted == False,
            Delivery.delivery_boy_id == None
        ).order_by(Delivery.created_at.asc())
    )
    deliveries = result.scalars().all()
    return [DeliveryResponse.model_validate(d) for d in deliveries]


# ─────────────────────────────────────────
# Sunday Collection
# ─────────────────────────────────────────

async def sunday_collection(
    payload: SundayCollectionRequest,
    db: AsyncSession,
    current_user: User,
) -> dict:
    if current_user.role not in [
        UserRole.DELIVERY_BOY,
        UserRole.ADMIN
    ]:
        raise PermissionException(
            "Only delivery boys can collect payments"
        )

    # User dhundo
    user_result = await db.execute(
        select(User).where(User.id == payload.user_id)
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise NotFoundException("User not found")

    collected = payload.amount_collected
    collection_type = payload.collection_type

    # Delivery charges collect
    if collection_type in ["delivery_charge", "all"]:
        charge_result = await db.execute(
            select(DeliveryChargeAccount).where(
                DeliveryChargeAccount.user_id == user.id
            )
        )
        charge_account = charge_result.scalar_one_or_none()

        if charge_account and charge_account.pending_amount > 0:
            charge_collected = min(
                collected,
                charge_account.pending_amount
            )
            charge_account.pending_amount -= charge_collected
            charge_account.total_paid += charge_collected
            charge_account.is_sunday_pending = (
                charge_account.pending_amount > 0
            )
            charge_account.last_sunday_collected = (
                datetime.utcnow()
            )
            user.total_delivery_charges_pending -= charge_collected

            if collection_type == "all":
                collected -= charge_collected

    # Udhaar collect
    if collection_type in ["udhaar", "all"]:
        udhaar_result = await db.execute(
            select(Udhaar).where(
                Udhaar.user_id == user.id,
                Udhaar.status.in_([
                    UdhaarStatus.PENDING,
                    UdhaarStatus.PARTIAL,
                    UdhaarStatus.OVERDUE
                ])
            ).order_by(Udhaar.created_at.asc())
        )
        udhaars = udhaar_result.scalars().all()

        remaining_to_collect = collected
        for udhaar in udhaars:
            if remaining_to_collect <= 0:
                break

            amount = min(
                remaining_to_collect,
                udhaar.amount_remaining
            )
            udhaar.amount_paid += amount
            udhaar.amount_remaining -= amount
            remaining_to_collect -= amount

            if udhaar.amount_remaining <= 0:
                udhaar.status = UdhaarStatus.COLLECTED
                udhaar.sunday_collected_by = current_user.id
                udhaar.sunday_collected_at = datetime.utcnow()
            else:
                udhaar.status = UdhaarStatus.PARTIAL

            user.total_udhaar_pending -= amount

    # User notification
    notification = Notification(
        id=uuid.uuid4(),
        user_id=user.id,
        title="Payment Collected ✅",
        body=(
            f"₹{payload.amount_collected} collect kiya gaya. "
            f"Shukriya!"
        ),
        type=NotificationType.SUNDAY_COLLECTION,
        data={
            "amount": payload.amount_collected,
            "type": collection_type
        }
    )
    db.add(notification)
    await db.commit()

    logger.info(
        f"Sunday collection: ₹{payload.amount_collected} "
        f"from {user.phone}"
    )

    return {
        "success": True,
        "message": f"₹{payload.amount_collected} collected!",
        "user": user.full_name,
        "phone": user.phone,
        "remaining_delivery_charges": (
            user.total_delivery_charges_pending
        ),
        "remaining_udhaar": user.total_udhaar_pending
    }


# ─────────────────────────────────────────
# Sunday Collection List
# ─────────────────────────────────────────

async def get_sunday_collection_list(
    db: AsyncSession,
    current_user: User,
) -> list:
    if current_user.role not in [
        UserRole.DELIVERY_BOY,
        UserRole.ADMIN
    ]:
        raise PermissionException("Access denied")

    # Pending charges wale users
    charge_result = await db.execute(
        select(DeliveryChargeAccount).where(
            DeliveryChargeAccount.is_sunday_pending == True,
            DeliveryChargeAccount.pending_amount > 0
        )
    )
    charge_accounts = charge_result.scalars().all()

    collection_list = []
    for account in charge_accounts:
        user_result = await db.execute(
            select(User).where(User.id == account.user_id)
        )
        user = user_result.scalar_one_or_none()
        if user:
            collection_list.append({
                "user_id": str(user.id),
                "name": user.full_name,
                "phone": user.phone,
                "address": user.address,
                "village": user.village,
                "delivery_charges_pending": (
                    account.pending_amount
                ),
                "udhaar_pending": user.total_udhaar_pending,
                "total_pending": (
                    account.pending_amount +
                    user.total_udhaar_pending
                )
            })

    # Sort by total pending
    collection_list.sort(
        key=lambda x: x["total_pending"],
        reverse=True
    )
    return collection_list
