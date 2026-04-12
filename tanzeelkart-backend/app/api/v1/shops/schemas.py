from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
import uuid


class CreateShopRequest(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    phone: str
    whatsapp: Optional[str] = None
    address: str
    village: Optional[str] = None
    latitude: float
    longitude: float
    opening_time: Optional[str] = "08:00"
    closing_time: Optional[str] = "21:00"
    is_open_sunday: Optional[bool] = True
    delivery_radius_km: Optional[float] = 2.0
    min_order_amount: Optional[float] = 0.0
    delivery_charge: Optional[float] = 20.0

    @field_validator("category")
    @classmethod
    def validate_category(cls, v):
        allowed = [
            "kirana", "agri", "medical",
            "hardware", "sabzi", "dairy",
            "electronic", "clothing", "other"
        ]
        if v not in allowed:
            raise ValueError("Invalid category")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        import re
        v = v.strip().replace(" ", "")
        if not re.match(r"^[6-9]\d{9}$", v):
            raise ValueError("Invalid phone number")
        return v


class UpdateShopRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    address: Optional[str] = None
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    is_open_sunday: Optional[bool] = None
    delivery_radius_km: Optional[float] = None
    min_order_amount: Optional[float] = None
    delivery_charge: Optional[float] = None
    is_delivery_available: Optional[bool] = None


class ShopResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    category: str
    status: str
    phone: str
    whatsapp: Optional[str]
    address: str
    village: Optional[str]
    block: Optional[str]
    district: Optional[str]
    latitude: float
    longitude: float
    shop_image: Optional[str]
    banner_image: Optional[str]
    is_delivery_available: bool
    delivery_radius_km: float
    min_order_amount: float
    delivery_charge: float
    opening_time: str
    closing_time: str
    is_open_sunday: bool
    total_orders: int
    rating: float
    total_reviews: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NearbyShopsRequest(BaseModel):
    latitude: float
    longitude: float
    radius_km: Optional[float] = 2.0
    category: Optional[str] = None


class ShopSearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
