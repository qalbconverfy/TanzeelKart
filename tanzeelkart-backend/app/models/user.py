from sqlalchemy import (
    Column, String, Boolean,
    Enum, Float, Text, Integer
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel


class UserRole(str, enum.Enum):
    BUYER = "buyer"
    SHOPKEEPER = "shopkeeper"
    DELIVERY_BOY = "delivery_boy"
    ADMIN = "admin"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class AccountType(str, enum.Enum):
    SHOP = "shop"
    MEDICAL = "medical"
    NORMAL = "normal"
    ALL_TYPES = "all_types"
    SKIP = "skip"
    ADMIN = "admin"


class User(BaseModel):
    __tablename__ = "users"

    # Basic Info
    full_name = Column(String(100), nullable=False)
    phone = Column(String(15), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=True)

    # Role
    role = Column(
        Enum(UserRole),
        default=UserRole.BUYER,
        nullable=False
    )
    status = Column(
        Enum(UserStatus),
        default=UserStatus.PENDING,
        nullable=False
    )

    # Account Type
    account_type = Column(
        Enum(AccountType),
        default=AccountType.SKIP,
        nullable=True
    )
    is_verified = Column(Boolean, default=False)
    verification_layer = Column(Integer, default=0)

    # Location
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    address = Column(Text, nullable=True)
    village = Column(String(100), nullable=True)
    block = Column(String(100), default="Reoti", nullable=True)
    district = Column(String(100), default="Ballia", nullable=True)
    state = Column(String(100), default="Uttar Pradesh", nullable=True)

    # Profile
    profile_image = Column(String(500), nullable=True)
    language = Column(String(10), default="hi", nullable=False)
    fcm_token = Column(String(500), nullable=True)

    # Verification
    is_phone_verified = Column(Boolean, default=False)
    is_email_verified = Column(Boolean, default=False)

    # Finance
    total_delivery_charges_pending = Column(Float, default=0.0)
    total_udhaar_pending = Column(Float, default=0.0)
    accumulated_delivery_charges = Column(Float, default=0.0)
    discount_percentage = Column(Float, default=0.0)

    # Relationships
    shop = relationship("Shop", back_populates="owner", uselist=False)
    orders = relationship("Order", back_populates="buyer")
    deliveries = relationship(
        "Delivery",
        back_populates="delivery_boy",
        foreign_keys="Delivery.delivery_boy_id"
    )
    udhaar_records = relationship("Udhaar", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
