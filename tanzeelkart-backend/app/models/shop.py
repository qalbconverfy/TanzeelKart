from sqlalchemy import (
    Column, String, Float,
    Boolean, Text, Integer, Enum
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel


class ShopCategory(str, enum.Enum):
    KIRANA = "kirana"
    AGRI = "agri"
    MEDICAL = "medical"
    HARDWARE = "hardware"
    SABZI = "sabzi"
    DAIRY = "dairy"
    ELECTRONIC = "electronic"
    CLOTHING = "clothing"
    OTHER = "other"


class ShopStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    SUSPENDED = "suspended"


class Shop(BaseModel):
    __tablename__ = "shops"

    # Basic
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    owner_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Category
    category = Column(
        Enum(ShopCategory),
        default=ShopCategory.KIRANA,
        nullable=False
    )
    status = Column(
        Enum(ShopStatus),
        default=ShopStatus.PENDING,
        nullable=False
    )

    # Location
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(Text, nullable=False)
    village = Column(String(100), nullable=True)
    block = Column(String(100), default="Reoti")
    district = Column(String(100), default="Ballia")

    # Contact
    phone = Column(String(15), nullable=False)
    whatsapp = Column(String(15), nullable=True)

    # Media
    shop_image = Column(String(500), nullable=True)
    banner_image = Column(String(500), nullable=True)

    # Delivery
    is_delivery_available = Column(Boolean, default=True)
    delivery_radius_km = Column(Float, default=2.0)
    min_order_amount = Column(Float, default=0.0)
    delivery_charge = Column(Float, default=20.0)

    # Timing
    opening_time = Column(String(10), default="08:00")
    closing_time = Column(String(10), default="21:00")
    is_open_sunday = Column(Boolean, default=True)

    # Stats
    total_orders = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)

    # Relationships
    owner = relationship("User", back_populates="shop")
    products = relationship("Product", back_populates="shop")
    orders = relationship("Order", back_populates="shop")
    