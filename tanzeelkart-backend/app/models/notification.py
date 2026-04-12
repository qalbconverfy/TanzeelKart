from sqlalchemy import (
    Column, String, Boolean,
    Enum, Text, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel


class NotificationType(str, enum.Enum):
    ORDER = "order"
    DELIVERY = "delivery"
    WEATHER = "weather"
    UDHAAR = "udhaar"
    PAYMENT = "payment"
    SYSTEM = "system"
    SUNDAY_COLLECTION = "sunday_collection"
    DELIVERY_CHARGE = "delivery_charge"


class Notification(BaseModel):
    __tablename__ = "notifications"

    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    type = Column(
        Enum(NotificationType),
        nullable=False
    )

    # Status
    is_read = Column(Boolean, default=False)

    # Extra data
    data = Column(JSON, nullable=True)

    # FCM
    is_sent = Column(Boolean, default=False)
    fcm_message_id = Column(String(200), nullable=True)

    # Relationships
    user = relationship("User", back_populates="notifications")
