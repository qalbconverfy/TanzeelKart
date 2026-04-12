from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
import uuid


class AddUdhaarRequest(BaseModel):
    shop_id: str
    amount: float
    due_days: Optional[int] = 7
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v

    @field_validator("due_days")
    @classmethod
    def validate_due_days(cls, v):
        if v < 1 or v > 30:
            raise ValueError("Due days must be between 1-30")
        return v


class PayUdhaarRequest(BaseModel):
    udhaar_id: str
    amount: float
    payment_method: str

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v

    @field_validator("payment_method")
    @classmethod
    def validate_method(cls, v):
        allowed = ["cash", "upi", "sunday_collection"]
        if v not in allowed:
            raise ValueError("Invalid payment method")
        return v


class UdhaarResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    shop_id: uuid.UUID
    order_id: Optional[uuid.UUID]
    total_amount: float
    amount_paid: float
    amount_remaining: float
    status: str
    due_date: Optional[datetime]
    is_overdue: bool
    is_sunday_collection: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UdhaarSummaryResponse(BaseModel):
    total_udhaar: float
    total_paid: float
    total_remaining: float
    overdue_amount: float
    udhaar_list: List[UdhaarResponse]


class DeliveryChargeResponse(BaseModel):
    total_accumulated: float
    total_paid: float
    pending_amount: float
    discount_percentage: float
    is_sunday_pending: bool
    last_sunday_collected: Optional[datetime]

    model_config = {"from_attributes": True}


class PayDeliveryChargeRequest(BaseModel):
    amount: float
    payment_method: str

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v
