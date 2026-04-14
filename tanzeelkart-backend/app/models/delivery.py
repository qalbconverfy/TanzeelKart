from sqlalchemy import (
    Column, String, Float,
    Enum, Text, DateTime,
    Boolean, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel


class DeliveryStatus(str, enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    PICKED = "picked"
    ON_WAY = "on_way"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Delivery(BaseModel):
    __tablename__ = "deliveries"

    # Relations ← ForeignKey add kiye
    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id"),
        nullable=False,
        index=True
    )
    delivery_boy_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )
    shop_id = Column(
        UUID(as_uuid=True),
        ForeignKey("shops.id"),
        nullable=False
    )
    buyer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    # Status
    status = Column(
        Enum(DeliveryStatus),
        default=DeliveryStatus.PENDING,
        nullable=False
    )

    # Location
    pickup_latitude = Column(Float, nullable=True)
    pickup_longitude = Column(Float, nullable=True)
    delivery_latitude = Column(Float, nullable=False)
    delivery_longitude = Column(Float, nullable=False)
    delivery_address = Column(Text, nullable=False)

    # Live location
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)

    # Timing
    assigned_at = Column(DateTime(timezone=True), nullable=True)
    picked_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    estimated_delivery_time = Column(
        DateTime(timezone=True), nullable=True
    )

    # Charge
    delivery_charge = Column(Float, default=0.0)
    is_charge_pending = Column(Boolean, default=False)

    # Notes
    delivery_notes = Column(Text, nullable=True)
    failure_reason = Column(Text, nullable=True)

    # Relationships
    order = relationship("Order", back_populates="delivery")
    delivery_boy = relationship(
        "User",
        back_populates="deliveries",
        foreign_keys=[delivery_boy_id]
    )
