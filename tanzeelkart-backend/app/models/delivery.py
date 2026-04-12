from sqlalchemy import (
    Column, String, Float,
    Enum, Text, DateTime, Boolean
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

    # Relations
    order_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    delivery_boy_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    shop_id = Column(UUID(as_uuid=True), nullable=False)
    buyer_id = Column(UUID(as_uuid=True), nullable=False)

    # Status
    status = Column(
        Enum(DeliveryStatus),
        default=DeliveryStatus.PENDING,
        nullable=False
    )

    # Location tracking
    pickup_latitude = Column(Float, nullable=True)
    pickup_longitude = Column(Float, nullable=True)
    delivery_latitude = Column(Float, nullable=False)
    delivery_longitude = Column(Float, nullable=False)
    delivery_address = Column(Text, nullable=False)

    # Delivery boy live location
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)

    # Timing
    assigned_at = Column(DateTime(timezone=True), nullable=True)
    picked_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    estimated_delivery_time = Column(DateTime(timezone=True), nullable=True)

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
