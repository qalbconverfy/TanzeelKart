import enum
from sqlalchemy import (
    Column, String, Boolean,
    Float, Integer, Enum, Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class UserRole(str, enum.Enum):
    BUYER = "buyer"
    SHOPKEEPER = "shopkeeper"
    DELIVERY_BOY = "delivery_boy"
    ADMIN = "admin"
    GUEST = "guest"


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


class LoginMethod(str, enum.Enum):
    PHONE = "phone"
    EMAIL = "email"
    GUEST = "guest"


class User(BaseModel):
    __tablename__ = "users"

    # ── Identity ─────────────────────────
    full_name = Column(
        String(100),
        nullable=False,
        default=""
    )
    phone = Column(
        String(15),
        unique=True,
        nullable=True,
        index=True,
    )
    email = Column(
        String(150),
        unique=True,
        nullable=True,
        index=True,
    )
    hashed_password = Column(
        String(255),
        nullable=True,
    )
    login_method = Column(
        Enum(LoginMethod),
        default=LoginMethod.PHONE,
        nullable=False,
    )
    is_guest = Column(Boolean, default=False)

    # ── Role & Status ─────────────────────
    role = Column(
        Enum(UserRole),
        default=UserRole.BUYER,
        nullable=False,
    )
    status = Column(
        Enum(UserStatus),
        default=UserStatus.ACTIVE,
        nullable=False,
    )
    account_type = Column(
        Enum(AccountType),
        default=AccountType.SKIP,
        nullable=True,
    )

    # ── Verification ──────────────────────
    is_phone_verified = Column(
        Boolean, default=False
    )
    is_email_verified = Column(
        Boolean, default=False
    )
    is_verified = Column(
        Boolean, default=False
    )
    verification_layer = Column(
        Integer, default=0
    )

    # ── Location ─────────────────────────
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    address = Column(Text, nullable=True)
    village = Column(String(100), nullable=True)
    block = Column(
        String(100),
        default="Reoti",
        nullable=True,
    )
    district = Column(
        String(100),
        default="Ballia",
        nullable=True,
    )
    state = Column(
        String(100),
        default="Uttar Pradesh",
        nullable=True,
    )

    # ── Profile ───────────────────────────
    profile_image = Column(
        String(500), nullable=True
    )
    language = Column(
        String(10),
        default="hi",
        nullable=False,
    )
    fcm_token = Column(
        String(500), nullable=True
    )

    # ── Finance ───────────────────────────
    total_delivery_charges_pending = Column(
        Float, default=0.0
    )
    total_udhaar_pending = Column(
        Float, default=0.0
    )
    accumulated_delivery_charges = Column(
        Float, default=0.0
    )
    discount_percentage = Column(
        Float, default=0.0
    )

    # ── Relationships ─────────────────────
    shop = relationship(
        "Shop",
        back_populates="owner",
        uselist=False,
    )
    orders = relationship(
        "Order",
        back_populates="buyer",
        foreign_keys="Order.buyer_id",
    )
    deliveries = relationship(
        "Delivery",
        back_populates="delivery_boy",
        foreign_keys="Delivery.delivery_boy_id",
    )
    wallet = relationship(
        "Wallet",
        back_populates="user",
        uselist=False,
    )
    udhaar_records = relationship(
        "Udhaar",
        back_populates="user",
        foreign_keys="Udhaar.user_id",
    )
    notifications = relationship(
        "Notification",
        back_populates="user",
    )
    verification = relationship(
        "Verification",
        back_populates="user",
        uselist=False,
    )
