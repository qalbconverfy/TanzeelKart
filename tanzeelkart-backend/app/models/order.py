from sqlalchemy import (
    Column, String, Float,
    Integer, Enum, Text,
    Boolean, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    PREPARING = "preparing"
    READY = "ready"
    PICKED = "picked"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    UPI = "upi"
    SPLIT = "split"
    UDHAAR = "udhaar"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    FAILED = "failed"


class Order(BaseModel):
    __tablename__ = "orders"

    # Relations ← ForeignKey add kiye
    buyer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    shop_id = Column(
        UUID(as_uuid=True),
        ForeignKey("shops.id"),
        nullable=False,
        index=True
    )
    delivery_id = Column(
        UUID(as_uuid=True),
        nullable=True
    )

    # Amount
    subtotal = Column(Float, nullable=False)
    delivery_charge = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)

    # Delivery Charge Logic
    delivery_charge_added_to_account = Column(
        Boolean, default=False
    )
    is_below_threshold = Column(Boolean, default=False)

    # Payment
    payment_method = Column(
        Enum(PaymentMethod),
        default=PaymentMethod.CASH,
        nullable=False
    )
    payment_status = Column(
        Enum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False
    )
    amount_paid_online = Column(Float, default=0.0)
    amount_paid_offline = Column(Float, default=0.0)
    amount_remaining = Column(Float, default=0.0)

    # Status
    status = Column(
        Enum(OrderStatus),
        default=OrderStatus.PENDING,
        nullable=False
    )

    # Delivery Address
    delivery_address = Column(Text, nullable=False)
    delivery_latitude = Column(Float, nullable=True)
    delivery_longitude = Column(Float, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    # Relationships
    buyer = relationship(
        "User",
        back_populates="orders",
        foreign_keys=[buyer_id]
    )
    shop = relationship("Shop", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    delivery = relationship(
        "Delivery",
        back_populates="order",
        uselist=False
    )
    udhaar = relationship(
        "Udhaar",
        back_populates="order",
        uselist=False
    )
