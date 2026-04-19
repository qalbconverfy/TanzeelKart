
from pydantic import BaseModel, field_validator
from typing import Optional
import re


class SendOTPRequest(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        v = v.strip().replace(" ", "").replace("+91", "")
        if not re.match(r"^[6-9]\d{9}$", v):
            raise ValueError("Valid Indian number daalo")
        return v


class VerifyOTPRequest(BaseModel):
    phone: str
    otp: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        return v.strip().replace(" ", "").replace("+91", "")

    @field_validator("otp")
    @classmethod
    def validate_otp(cls, v):
        v = str(v).strip()
        if not v.isdigit() or len(v) != 6:
            raise ValueError("OTP 6 digits ka hona chahiye")
        return v


class EmailRegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, v):
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Naam 2+ characters chahiye")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        v = v.strip().lower()
        if not re.match(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            v,
        ):
            raise ValueError("Valid email daalo")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password 6+ characters chahiye")
        return v


class EmailLoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        return v.strip().lower()


class SelectAccountTypeRequest(BaseModel):
    account_type: str

    @field_validator("account_type")
    @classmethod
    def validate_type(cls, v):
        allowed = [
            "shop", "medical", "normal",
            "all_types", "skip",
        ]
        if v not in allowed:
            raise ValueError("Invalid account type")
        return v


class ShopVerifyLayer1(BaseModel):
    shop_owner_name: str
    seller_name: str

    @field_validator("shop_owner_name", "seller_name")
    @classmethod
    def validate_names(cls, v):
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Naam 2+ characters chahiye")
        return v


class ShopVerifyLayer2(BaseModel):
    shop_code: str

    @field_validator("shop_code")
    @classmethod
    def validate_code(cls, v):
        v = v.strip().upper()
        if not re.match(r"^TK-\d{4}-\d{5}$", v):
            raise ValueError(
                "Valid shop code daalo (TK-2026-XXXXX)"
            )
        return v


class MedicalVerifyRequest(BaseModel):
    layer: int
    license_number: Optional[str] = None
    pharmacist_name: Optional[str] = None
    registration_number: Optional[str] = None
    document_url: Optional[str] = None


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminOTPVerify(BaseModel):
    username: str
    otp: str


class AdminBiometricVerify(BaseModel):
    username: str
    biometric_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


# Responses
class OTPResponse(BaseModel):
    success: bool
    message: str
    phone: str


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
