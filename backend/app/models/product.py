import enum
from sqlalchemy import (
    Column, String, Float, Boolean,
    Text, Integer, Enum, ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class ProductStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"


class ProductUnit(str, enum.Enum):
    KG = "kg"
    GRAM = "gram"
    LITRE = "litre"
    ML = "ml"
    PIECE = "piece"
    DOZEN = "dozen"
    PACKET = "packet"
    BOTTLE = "bottle"
    BOX = "box"
    METER = "meter"


class Product(BaseModel):
    __tablename__ = "products"

    name = Column(
        String(200),
        nullable=False,
        index=True,
    )
    description = Column(Text, nullable=True)

    shop_id = Column(
        UUID(as_uuid=True),
        ForeignKey("shops.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    price = Column(Float, nullable=False)
    discount_price = Column(Float, nullable=True)

    unit = Column(
        Enum(ProductUnit),
        default=ProductUnit.PIECE,
        nullable=False,
    )

    stock = Column(Integer, default=0)
    min_order_qty = Column(Integer, default=1)
    max_order_qty = Column(Integer, default=100)

    status = Column(
        Enum(ProductStatus),
        default=ProductStatus.ACTIVE,
        nullable=False,
    )

    image = Column(String(500), nullable=True)
    tags = Column(String(500), nullable=True)
    total_orders = Column(Integer, default=0)
    rating = Column(Float, default=0.0)

    # Relationships
    shop = relationship(
        "Shop", back_populates="products"
    )
    order_items = relationship(
        "OrderItem", back_populates="product"
    )
