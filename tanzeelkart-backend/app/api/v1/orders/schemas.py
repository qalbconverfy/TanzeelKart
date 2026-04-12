from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
import uuid


class OrderItemRequest(BaseModel):
    product_id: str
    quantity: int

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v


class CreateOrderRequest(BaseModel):
    shop_id: str
    items: List[OrderItemRequest]
    delivery_address: str
    delivery_latitude: Optional[float] = None
    delivery_longitude: Optional[float] = None
    payment_method: str
    amount_paid_online: Optional[float] = 0.0
    notes: Optional[str] = None
    is_udhaar: Optional[bool] = False

    @field_validator("payment_method")
    @classmethod
    def validate_payment(cls, v):
        allowed = ["cash", "upi", "split", "udhaar"]
        if v not in allowed:
            raise ValueError("Invalid payment method")
        return v

    @field_validator("items")
    @classmethod
    def validate_items(cls, v):
        if len(v) == 0:
            raise ValueError("Order must have at least 1 item")
        return v


class UpdateOrderStatusRequest(BaseModel):
    status: str
    notes: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        allowed = [
            "accepted", "preparing",
            "ready", "cancelled"
        ]
        if v not in allowed:
            raise ValueError("Invalid status")
        return v


class CancelOrderRequest(BaseModel):
    reason: str


class OrderItemResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    product_name: str
    product_price: float
    quantity: int
    subtotal: float

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: uuid.UUID
    buyer_id: uuid.UUID
    shop_id: uuid.UUID
    status: str
    subtotal: float
    delivery_charge: float
    discount: float
    total_amount: float
    payment_method: str
    payment_status: str
    amount_paid_online: float
    amount_paid_offline: float
    amount_remaining: float
    delivery_charge_added_to_account: bool
    is_below_threshold: bool
    delivery_address: str
    notes: Optional[str]
    items: List[OrderItemResponse]
    created_at: datetime

    model_config = {"from_attributes": True}
