from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
import uuid


class AddAdminRequest(BaseModel):
    user_phone: str
    username: str
    password: str
    is_super_admin: Optional[bool] = False
    permissions: Optional[dict] = None


class VerifyShopRequest(BaseModel):
    shop_id: str
    status: str
    notes: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v not in ["verified", "rejected"]:
            raise ValueError("Invalid status")
        return v


class VerifyMedicalRequest(BaseModel):
    user_id: str
    status: str
    notes: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v not in ["approved", "rejected"]:
            raise ValueError("Invalid status")
        return v


class AdminStatsResponse(BaseModel):
    total_users: int
    total_shops: int
    total_orders: int
    total_deliveries: int
    pending_shop_verifications: int
    pending_medical_verifications: int
    total_udhaar_pending: float
    total_delivery_charges_pending: float


class PlatformSettingsRequest(BaseModel):
    min_order_for_delivery_charge: Optional[float] = None
    max_delivery_radius_km: Optional[float] = None
    delivery_charge_discount_threshold: Optional[float] = None
