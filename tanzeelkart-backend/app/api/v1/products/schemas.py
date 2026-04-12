from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
import uuid


class CreateProductRequest(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    discount_price: Optional[float] = None
    unit: str
    stock: int
    min_order_qty: Optional[int] = 1
    max_order_qty: Optional[int] = 100
    tags: Optional[str] = None

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v

    @field_validator("stock")
    @classmethod
    def validate_stock(cls, v):
        if v < 0:
            raise ValueError("Stock cannot be negative")
        return v

    @field_validator("unit")
    @classmethod
    def validate_unit(cls, v):
        allowed = [
            "kg", "gram", "litre",
            "ml", "piece", "dozen",
            "packet", "bottle"
        ]
        if v not in allowed:
            raise ValueError("Invalid unit")
        return v

    @field_validator("discount_price")
    @classmethod
    def validate_discount(cls, v, info):
        if v and "price" in info.data:
            if v >= info.data["price"]:
                raise ValueError(
                    "Discount price must be less than price"
                )
        return v


class UpdateProductRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    discount_price: Optional[float] = None
    unit: Optional[str] = None
    stock: Optional[int] = None
    min_order_qty: Optional[int] = None
    max_order_qty: Optional[int] = None
    tags: Optional[str] = None
    status: Optional[str] = None


class ProductResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    shop_id: uuid.UUID
    price: float
    discount_price: Optional[float]
    unit: str
    stock: int
    min_order_qty: int
    max_order_qty: int
    status: str
    image: Optional[str]
    tags: Optional[str]
    total_orders: int
    rating: float
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    per_page: int
