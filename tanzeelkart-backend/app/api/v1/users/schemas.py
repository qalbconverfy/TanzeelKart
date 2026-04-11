from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid


class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    village: Optional[str] = None
    language: Optional[str] = None
    profile_image: Optional[str] = None


class UserResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    phone: str
    email: Optional[str]
    role: str
    status: str
    latitude: Optional[float]
    longitude: Optional[float]
    address: Optional[str]
    village: Optional[str]
    block: Optional[str]
    district: Optional[str]
    profile_image: Optional[str]
    is_phone_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserFinanceResponse(BaseModel):
    total_delivery_charges_pending: float
    total_udhaar_pending: float
    accumulated_delivery_charges: float
    discount_percentage: float
    is_sunday_collection_pending: bool


class FCMTokenRequest(BaseModel):
    fcm_token: str
    