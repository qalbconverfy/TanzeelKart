import enum
from sqlalchemy import (
    Column, String, Boolean,
    Enum, Text, JSON, Integer, ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    LAYER_1 = "layer_1"
    LAYER_2 = "layer_2"
    LAYER_3 = "layer_3"
    LAYER_4 = "layer_4"
    LAYER_5 = "layer_5"
    APPROVED = "approved"
    REJECTED = "rejected"


class VerificationType(str, enum.Enum):
    SHOP = "shop"
    MEDICAL = "medical"
    ADMIN = "admin"


class Verification(BaseModel):
    __tablename__ = "verifications"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    type = Column(
        Enum(VerificationType),
        nullable=False,
    )
    status = Column(
        Enum(VerificationStatus),
        default=VerificationStatus.PENDING,
    )
    current_layer = Column(Integer, default=0)
    total_layers = Column(Integer, nullable=False)

    # Shop fields
    shop_owner_name = Column(
        String(200), nullable=True
    )
    seller_name = Column(
        String(200), nullable=True
    )
    shop_code = Column(
        String(50), nullable=True, index=True
    )

    # Medical fields
    license_number = Column(
        String(100), nullable=True
    )
    pharmacist_name = Column(
        String(200), nullable=True
    )
    registration_number = Column(
        String(100), nullable=True
    )
    documents = Column(JSON, nullable=True)

    # Admin review
    reviewed_by = Column(
        UUID(as_uuid=True), nullable=True
    )
    rejection_reason = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False)

    # Relationship
    user = relationship(
        "User", back_populates="verification"
    )
