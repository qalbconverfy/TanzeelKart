from sqlalchemy import (
    Column, String, Enum,
    Boolean, Text, JSON, Integer
)
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.models.base import BaseModel


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    LAYER_1 = "layer_1_complete"
    LAYER_2 = "layer_2_complete"
    LAYER_3 = "layer_3_complete"
    LAYER_4 = "layer_4_complete"
    LAYER_5 = "layer_5_complete"
    APPROVED = "approved"
    REJECTED = "rejected"


class VerificationType(str, enum.Enum):
    SHOP = "shop"
    MEDICAL = "medical"
    ADMIN = "admin"


class Verification(BaseModel):
    __tablename__ = "verifications"

    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    type = Column(Enum(VerificationType), nullable=False)
    status = Column(
        Enum(VerificationStatus),
        default=VerificationStatus.PENDING
    )
    current_layer = Column(Integer, default=0)
    total_layers = Column(Integer, nullable=False)

    # Shop verification data
    shop_owner_name = Column(String(200), nullable=True)
    seller_name = Column(String(200), nullable=True)
    shop_id = Column(String(50), nullable=True, unique=True, index=True)

    # Medical verification data
    license_number = Column(String(100), nullable=True)
    pharmacist_name = Column(String(200), nullable=True)
    registration_number = Column(String(100), nullable=True)
    documents = Column(JSON, nullable=True)

    # Admin approval
    reviewed_by = Column(UUID(as_uuid=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)

    is_verified = Column(Boolean, default=False)
