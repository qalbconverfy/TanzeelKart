import enum
from sqlalchemy import (
    Column, Float, Boolean,
    Enum, Text, DateTime,
    String, ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class UdhaarStatus(str, enum.Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"
    COLLECTED = "collected"


class Udhaar(BaseModel):
    __tablename__ = "udhaar"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    shop_id = Column(
        UUID(as_uuid=True),
        ForeignKey("shops.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="SET NULL"),
        nullable=True,
    )

    total_amount = Column(Float, nullable=False)
    amount_paid = Column(Float, default=0.0)
    amount_remaining = Column(Float, nullable=False)

    status = Column(
        Enum(UdhaarStatus),
        default=UdhaarStatus.PENDING,
        nullable=False,
    )

    due_date = Column(
        DateTime(timezone=True), nullable=True
    )
    is_overdue = Column(Boolean, default=False)
    is_sunday_collection = Column(
        Boolean, default=False
    )
    sunday_collected_by = Column(
        UUID(as_uuid=True), nullable=True
    )
    sunday_collected_at = Column(
        DateTime(timezone=True), nullable=True
    )
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship(
        "User",
        back_populates="udhaar_records",
        foreign_keys=[user_id],
    )
    order = relationship(
        "Order",
        back_populates="udhaar",
        foreign_keys=[order_id],
    )


class DeliveryChargeAccount(BaseModel):
    __tablename__ = "delivery_charge_accounts"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    total_accumulated = Column(Float, default=0.0)
    total_paid = Column(Float, default=0.0)
    pending_amount = Column(Float, default=0.0)
    discount_percentage = Column(Float, default=0.0)
    is_sunday_pending = Column(Boolean, default=False)
    last_collected_at = Column(
        DateTime(timezone=True), nullable=True
    )
