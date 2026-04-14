from sqlalchemy import (
    Column, Float, Integer,
    String, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class OrderItem(BaseModel):
    __tablename__ = "order_items"

    # ← ForeignKey add kiye
    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id"),
        nullable=False,
        index=True
    )
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )
    shop_id = Column(
        UUID(as_uuid=True),
        ForeignKey("shops.id"),
        nullable=False
    )

    # Product snapshot
    product_name = Column(String(200), nullable=False)
    product_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    subtotal = Column(Float, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship(
        "Product",
        back_populates="order_items"
    )
