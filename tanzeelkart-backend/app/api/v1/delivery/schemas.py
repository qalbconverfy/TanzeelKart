
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
import uuid


class AssignDeliveryRequest(BaseModel):
    order_id: str


class UpdateDeliveryStatusRequest(BaseModel):
    status: str
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None
    notes: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        allowed = [
            "picked", "on_way",
            "delivered", "failed"
        ]
        if v not in allowed:
            raise ValueError("Invalid status")
        return v


class UpdateLocationRequest(BaseModel):
    latitude: float
    longitude: float


class CollectPaymentRequest(BaseModel):
    delivery_id: str
    amount_collected: float
    payment_type: str

    @field_validator("payment_type")
    @classmethod
    def validate_type(cls, v):
        allowed = [
            "delivery_charge",
            "udhaar",
            "order_payment",
            "all"
        ]
        if v not in allowed:
            raise ValueError("Invalid payment type")
        return v


class SundayCollectionRequest(BaseModel):
    user_id: str
    amount_collected: float
    collection_type: str
    notes: Optional[str] = None

    @field_validator("collection_type")
    @classmethod
    def validate_type(cls, v):
        allowed = ["delivery_charge", "udhaar", "all"]
        if v not in allowed:
            raise ValueError("Invalid collection type")
        return v


class DeliveryResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    delivery_boy_id: Optional[uuid.UUID]
    shop_id: uuid.UUID
    buyer_id: uuid.UUID
    status: str
    pickup_latitude: Optional[float]
    pickup_longitude: Optional[float]
    delivery_latitude: float
    delivery_longitude: float
    delivery_address: str
    current_latitude: Optional[float]
    current_longitude: Optional[float]
    delivery_charge: float
    is_charge_pending: bool
    assigned_at: Optional[datetime]
    picked_at: Optional[datetime]
    delivered_at: Optional[datetime]
    estimated_delivery_time: Optional[datetime]
    delivery_notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
