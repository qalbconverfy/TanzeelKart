from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.order import (
    Order, OrderStatus,
    PaymentMethod, PaymentStatus
)
from app.models.order_item import OrderItem
from app.models.product import Product, ProductStatus
from app.models.shop import Shop
from app.models.user import User
from app.models.udhaar import Udhaar, UdhaarStatus, DeliveryChargeAccount
from app.models.notification import Notification, NotificationType
from app.api.v1.orders.schemas import (
    CreateOrderRequest,
    UpdateOrderStatusRequest,
    CancelOrderRequest,
    OrderResponse
)
from app.core.config import settings
from app.core.exceptions import (
    NotFoundException,
    ValidationException,
    PermissionException
)
from loguru import logger
from datetime import datetime, timedelta
import uuid


# ─────────────────────────────────────────
# Delivery Charge Calculator
# ─────────────────────────────────────────

async def calculate_delivery_charge(
    subtotal: float,
    shop: Shop,
    user: User,
    db: AsyncSession,
) -> dict:
    base_charge = shop.delivery_charge
    threshold = settings.MIN_ORDER_FOR_DELIVERY_CHARGE

    # User ka discount
    discount_pct = user.discount_percentage or 0.0
    discounted_charge = base_charge * (1 - discount_pct / 100)

    if subtotal >= threshold:
        # Normal charge lagega
        return {
            "charge": round(discounted_charge, 2),
            "add_to_account": False,
            "is_below_threshold": False,
        }
    else:
        # Charge account mein add hoga
        return {
            "charge": round(discounted_charge, 2),
            "add_to_account": True,
            "is_below_threshold": True,
        }


# ─────────────────────────────────────────
# Discount Calculator
# ─────────────────────────────────────────

async def update_discount(
    user: User,
    db: AsyncSession,
) -> None:
    accumulated = user.accumulated_delivery_charges

    if accumulated >= 2000:
        user.discount_percentage = 20.0
    elif accumulated >= 1000:
        user.discount_percentage = 15.0
    elif accumulated >= 500:
        user.discount_percentage = 10.0
    else:
        user.discount_percentage = 0.0


# ─────────────────────────────────────────
# Create Order
# ─────────────────────────────────────────

async def create_order(
    payload: CreateOrderRequest,
    db: AsyncSession,
    current_user: User,
) -> dict:
    # Shop check
    shop_result = await db.execute(
        select(Shop).where(
            Shop.id == payload.shop_id,
            Shop.is_deleted == False,
            Shop.is_active == True
        )
    )
    shop = shop_result.scalar_one_or_none()
    if not shop:
        raise NotFoundException("Shop not found")

    # Items validate + subtotal calculate
    subtotal = 0.0
    order_items = []

    for item_req in payload.items:
        product_result = await db.execute(
            select(Product).where(
                Product.id == item_req.product_id,
                Product.shop_id == shop.id,
                Product.is_deleted == False,
                Product.is_active == True
            )
        )
        product = product_result.scalar_one_or_none()
        if not product:
            raise NotFoundException(
                f"Product {item_req.product_id} not found"
            )

        if product.status == ProductStatus.OUT_OF_STOCK:
            raise ValidationException(
                f"{product.name} is out of stock"
            )

        if item_req.quantity < product.min_order_qty:
            raise ValidationException(
                f"Minimum order for {product.name} "
                f"is {product.min_order_qty}"
            )

        if item_req.quantity > product.stock:
            raise ValidationException(
                f"Only {product.stock} units available "
                f"for {product.name}"
            )

        price = product.discount_price or product.price
        item_subtotal = price * item_req.quantity
        subtotal += item_subtotal

        order_items.append({
            "product": product,
            "quantity": item_req.quantity,
            "price": price,
            "subtotal": item_subtotal
        })

    # Delivery charge calculate
    delivery_info = await calculate_delivery_charge(
        subtotal, shop, current_user, db
    )

    # Payment calculate
    total_amount = subtotal + (
        0 if delivery_info["add_to_account"]
        else delivery_info["charge"]
    )

    amount_paid_online = payload.amount_paid_online or 0.0
    amount_remaining = total_amount - amount_paid_online

    # Payment status
    if payload.is_udhaar:
        payment_method = PaymentMethod.UDHAAR
        payment_status = PaymentStatus.PENDING
    elif amount_paid_online >= total_amount:
        payment_method = PaymentMethod.UPI
        payment_status = PaymentStatus.PAID
        amount_remaining = 0.0
    elif amount_paid_online > 0:
        payment_method = PaymentMethod.SPLIT
        payment_status = PaymentStatus.PARTIAL
    else:
        payment_method = PaymentMethod.CASH
        payment_status = PaymentStatus.PENDING

    # Order create
    order = Order(
        id=uuid.uuid4(),
        buyer_id=current_user.id,
        shop_id=shop.id,
        subtotal=subtotal,
        delivery_charge=delivery_info["charge"],
        discount=0.0,
        total_amount=total_amount,
        payment_method=payment_method,
        payment_status=payment_status,
        amount_paid_online=amount_paid_online,
        amount_paid_offline=0.0,
        amount_remaining=amount_remaining,
        delivery_charge_added_to_account=delivery_info["add_to_account"],
        is_below_threshold=delivery_info["is_below_threshold"],
        status=OrderStatus.PENDING,
        delivery_address=payload.delivery_address,
        delivery_latitude=payload.delivery_latitude,
        delivery_longitude=payload.delivery_longitude,
        notes=payload.notes,
    )
    db.add(order)
    await db.flush()

    # Order items create
    for item in order_items:
        order_item = OrderItem(
            id=uuid.uuid4(),
            order_id=order.id,
            product_id=item["product"].id,
            shop_id=shop.id,
            product_name=item["product"].name,
            product_price=item["price"],
            quantity=item["quantity"],
            subtotal=item["subtotal"]
        )
        db.add(order_item)

        # Stock reduce karo
        item["product"].stock -= item["quantity"]
        item["product"].total_orders += 1

    # Delivery charge account mein add karo
    if delivery_info["add_to_account"]:
        current_user.total_delivery_charges_pending += delivery_info["charge"]
        current_user.accumulated_delivery_charges += delivery_info["charge"]

        # Charge account update
        charge_result = await db.execute(
            select(DeliveryChargeAccount).where(
                DeliveryChargeAccount.user_id == current_user.id
            )
        )
        charge_account = charge_result.scalar_one_or_none()

        if not charge_account:
            charge_account = DeliveryChargeAccount(
                user_id=current_user.id,
                total_accumulated=delivery_info["charge"],
                pending_amount=delivery_info["charge"],
                is_sunday_pending=True,
            )
            db.add(charge_account)
        else:
            charge_account.total_accumulated += delivery_info["charge"]
            charge_account.pending_amount += delivery_info["charge"]
            charge_account.is_sunday_pending = True

        # Discount update
        await update_discount(current_user, db)

        # Notification bhejo
        notification = Notification(
            id=uuid.uuid4(),
            user_id=current_user.id,
            title="Delivery Charge Added",
            body=(
                f"₹{delivery_info['charge']} delivery charge "
                f"aapke account mein add hua. "
                f"Total pending: "
                f"₹{current_user.total_delivery_charges_pending}"
            ),
            type=NotificationType.DELIVERY_CHARGE,
            data={
                "charge": delivery_info["charge"],
                "total_pending": current_user.total_delivery_charges_pending
            }
        )
        db.add(notification)

    # Udhaar create
    if payload.is_udhaar:
        due_date = datetime.utcnow() + timedelta(days=7)
        udhaar = Udhaar(
            id=uuid.uuid4(),
            user_id=current_user.id,
            shop_id=shop.id,
            order_id=order.id,
            total_amount=total_amount,
            amount_paid=amount_paid_online,
            amount_remaining=amount_remaining,
            status=UdhaarStatus.PENDING,
            due_date=due_date,
            is_sunday_collection=True,
        )
        db.add(udhaar)
        current_user.total_udhaar_pending += amount_remaining

        notification = Notification(
            id=uuid.uuid4(),
            user_id=current_user.id,
            title="Udhaar Added",
            body=(
                f"₹{amount_remaining} ka udhaar add hua "
                f"— {shop.name}. Due: Sunday"
            ),
            type=NotificationType.UDHAAR,
            data={
                "amount": amount_remaining,
                "shop": shop.name,
                "due_date": str(due_date)
            }
        )
        db.add(notification)

    # Shop order count
    shop.total_orders += 1

    # Shopkeeper notification
    shopkeeper_notification = Notification(
        id=uuid.uuid4(),
        user_id=shop.owner_id,
        title="Naya Order! 🛒",
        body=(
            f"Aapke shop mein naya order aaya! "
            f"Total: ₹{total_amount}"
        ),
        type=NotificationType.ORDER,
        data={
            "order_id": str(order.id),
            "amount": total_amount
        }
    )
    db.add(shopkeeper_notification)

    await db.commit()
    await db.refresh(order)

    logger.info(
        f"Order created: {order.id} "
        f"— ₹{total_amount}"
    )

    return {
        "success": True,
        "message": "Order placed successfully!",
        "order_id": str(order.id),
        "total_amount": total_amount,
        "delivery_charge": delivery_info["charge"],
        "delivery_charge_added_to_account": delivery_info["add_to_account"],
        "payment_status": payment_status.value,
        "amount_remaining": amount_remaining,
    }


# ─────────────────────────────────────────
# Get My Orders (Buyer)
# ─────────────────────────────────────────

async def get_my_orders(
    db: AsyncSession,
    current_user: User,
    page: int = 1,
    per_page: int = 20,
) -> list:
    offset = (page - 1) * per_page
    result = await db.execute(
        select(Order).where(
            Order.buyer_id == current_user.id,
            Order.is_deleted == False
        ).order_by(
            Order.created_at.desc()
        ).offset(offset).limit(per_page)
    )
    orders = result.scalars().all()
    return [OrderResponse.model_validate(o) for o in orders]


# ─────────────────────────────────────────
# Get Shop Orders (Shopkeeper)
# ─────────────────────────────────────────

async def get_shop_orders(
    db: AsyncSession,
    current_user: User,
    status: str = None,
    page: int = 1,
    per_page: int = 20,
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

    offset = (page - 1) * per_page
    query = select(Order).where(
        Order.shop_id == shop.id,
        Order.is_deleted == False
    )

    if status:
        query = query.where(
            Order.status == OrderStatus(status)
        )

    result = await db.execute(
        query.order_by(
            Order.created_at.desc()
        ).offset(offset).limit(per_page)
    )
    orders = result.scalars().all()
    return [OrderResponse.model_validate(o) for o in orders]


# ─────────────────────────────────────────
# Update Order Status (Shopkeeper)
# ─────────────────────────────────────────

async def update_order_status(
    order_id: str,
    payload: UpdateOrderStatusRequest,
    db: AsyncSession,
    current_user: User,
) -> dict:
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
        select(Order).where(
            Order.id == order_id,
            Order.shop_id == shop.id,
            Order.is_deleted == False
        )
    )
    order = result.scalar_one_or_none()
    if not order:
        raise NotFoundException("Order not found")

    order.status = OrderStatus(payload.status)

    # Buyer ko notification
    notification = Notification(
        id=uuid.uuid4(),
        user_id=order.buyer_id,
        title="Order Update",
        body=f"Aapka order {payload.status} ho gaya!",
        type=NotificationType.ORDER,
        data={
            "order_id": str(order.id),
            "status": payload.status
        }
    )
    db.add(notification)
    await db.commit()

    return {
        "success": True,
        "message": f"Order {payload.status}",
        "order_id": order_id
    }


# ─────────────────────────────────────────
# Cancel Order
# ─────────────────────────────────────────

async def cancel_order(
    order_id: str,
    payload: CancelOrderRequest,
    db: AsyncSession,
    current_user: User,
) -> dict:
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.buyer_id == current_user.id,
            Order.is_deleted == False
        )
    )
    order = result.scalar_one_or_none()
    if not order:
        raise NotFoundException("Order not found")

    if order.status not in [
        OrderStatus.PENDING,
        OrderStatus.ACCEPTED
    ]:
        raise ValidationException(
            "Order cannot be cancelled at this stage"
        )

    order.status = OrderStatus.CANCELLED
    order.cancellation_reason = payload.reason

    # Stock wapas karo
    items_result = await db.execute(
        select(OrderItem).where(
            OrderItem.order_id == order.id
        )
    )
    items = items_result.scalars().all()

    for item in items:
        product_result = await db.execute(
            select(Product).where(
                Product.id == item.product_id
            )
        )
        product = product_result.scalar_one_or_none()
        if product:
            product.stock += item.quantity

    await db.commit()
    logger.info(f"Order cancelled: {order_id}")

    return {
        "success": True,
        "message": "Order cancelled successfully"
    }


# ─────────────────────────────────────────
# Get Order Detail
# ─────────────────────────────────────────

async def get_order_detail(
    order_id: str,
    db: AsyncSession,
    current_user: User,
) -> OrderResponse:
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.is_deleted == False
        )
    )
    order = result.scalar_one_or_none()
    if not order:
        raise NotFoundException("Order not found")

    # Check access
    shop_result = await db.execute(
        select(Shop).where(
            Shop.owner_id == current_user.id
        )
    )
    shop = shop_result.scalar_one_or_none()

    is_buyer = order.buyer_id == current_user.id
    is_shopkeeper = shop and order.shop_id == shop.id

    if not is_buyer and not is_shopkeeper:
        raise PermissionException("Access denied")

    return OrderResponse.model_validate(order)
