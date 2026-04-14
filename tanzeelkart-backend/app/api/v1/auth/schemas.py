from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional, List
from datetime import datetime
import uuid


class SendOTPRequest(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        import re
        v = v.strip().replace(" ", "")
        if not re.match(r"^[6-9]\d{9}$", v):
            raise ValueError("Invalid Indian phone number")
        return v


class OTPResponse(BaseModel):
    success: bool
    message: str
    phone: str


class VerifyOTPRequest(BaseModel):
    phone: str
    otp: str

    @field_validator("otp")
    @classmethod
    def validate_otp(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError("OTP must be 6 digits")
        return v


class TokenResponse(BaseModel):
    success: bool
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    role: str
    account_type: Optional[str] = None
    is_new_user: bool = False
    is_verified: bool = False
    is_guest: bool = False


class SelectAccountTypeRequest(BaseModel):
    user_id: str
    account_type: str

    @field_validator("account_type")
    @classmethod
    def validate_type(cls, v):
        allowed = [
            "shop", "medical",
            "normal", "all_types", "skip"
        ]
        if v not in allowed:
            raise ValueError("Invalid account type")
        return v


# ── Email ─────────────────────────────────

class EmailRegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        import re
        v = v.strip().lower()
        if not re.match(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            v
        ):
            raise ValueError("Invalid email address")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError(
                "Password 6+ characters hona chahiye"
            )
        return v

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError("Naam 2+ characters ka hona chahiye")
        return v.strip()


class EmailLoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        return v.strip().lower()


# ── Shop Verification ─────────────────────

class ShopVerificationLayer1(BaseModel):
    shop_owner_name: str
    seller_name: str


class ShopVerificationLayer2(BaseModel):
    shop_id: str


# ── Medical Verification ──────────────────

class MedicalVerificationLayer1(BaseModel):
    license_number: str


class MedicalVerificationLayer2(BaseModel):
    pharmacist_name: str


class MedicalVerificationLayer3(BaseModel):
    registration_number: str


class MedicalVerificationLayer4(BaseModel):
    document_url: str


# ── Admin ─────────────────────────────────

class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminOTPVerify(BaseModel):
    username: str
    otp: str


class AdminBiometricVerify(BaseModel):
    username: str
    biometric_token: str


# ── Token ─────────────────────────────────

class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str
