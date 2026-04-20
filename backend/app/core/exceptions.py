from fastapi import HTTPException, status


# ─── Base ──────────────────────────────────────────────────────────────────────
class TanzeelKartException(Exception):
    """Base exception for all TanzeelKart custom errors."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


# ─── Auth Exceptions ───────────────────────────────────────────────────────────
class InvalidCredentialsException(HTTPException):
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": detail},
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenExpiredException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "TOKEN_EXPIRED", "message": "Token has expired"},
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenInvalidException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "TOKEN_INVALID", "message": "Token is invalid"},
            headers={"WWW-Authenticate": "Bearer"},
        )


class InsufficientPermissionsException(HTTPException):
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": detail},
        )


class AccountLockedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_423_LOCKED,
            detail={"code": "ACCOUNT_LOCKED", "message": "Account locked due to multiple failed attempts"},
        )


# ─── OTP Exceptions ────────────────────────────────────────────────────────────
class OTPInvalidException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "OTP_INVALID", "message": "Invalid or expired OTP"},
        )


class OTPResendCooldownException(HTTPException):
    def __init__(self, seconds_remaining: int):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "OTP_COOLDOWN",
                "message": f"Please wait {seconds_remaining} seconds before resending OTP",
                "retry_after": seconds_remaining,
            },
        )


class OTPMaxAttemptsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"code": "OTP_MAX_ATTEMPTS", "message": "Maximum OTP attempts exceeded. Request a new OTP."},
        )


# ─── User Exceptions ───────────────────────────────────────────────────────────
class UserNotFoundException(HTTPException):
    def __init__(self, detail: str = "User not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": detail},
        )


class UserAlreadyExistsException(HTTPException):
    def __init__(self, field: str = "phone"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "USER_EXISTS", "message": f"User with this {field} already exists"},
        )


# ─── Shop Exceptions ───────────────────────────────────────────────────────────
class ShopNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "SHOP_NOT_FOUND", "message": "Shop not found"},
        )


class ShopNotVerifiedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "SHOP_NOT_VERIFIED", "message": "Shop is not verified yet"},
        )


class ShopAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "SHOP_EXISTS", "message": "A shop with this phone number already exists"},
        )


# ─── Product Exceptions ────────────────────────────────────────────────────────
class ProductNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PRODUCT_NOT_FOUND", "message": "Product not found"},
        )


class OutOfStockException(HTTPException):
    def __init__(self, product_name: str = "Product"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "OUT_OF_STOCK", "message": f"{product_name} is out of stock"},
        )


# ─── Order Exceptions ──────────────────────────────────────────────────────────
class OrderNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ORDER_NOT_FOUND", "message": "Order not found"},
        )


class OrderStatusException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "ORDER_STATUS_ERROR", "message": detail},
        )


# ─── Delivery Exceptions ───────────────────────────────────────────────────────
class DeliveryRadiusException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "OUT_OF_DELIVERY_RADIUS", "message": "Delivery address is outside the 2km delivery radius"},
        )


# ─── Payment / Udhaar Exceptions ───────────────────────────────────────────────
class UdhaarNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "UDHAAR_NOT_FOUND", "message": "Udhaar record not found"},
        )


class InsufficientBalanceException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INSUFFICIENT_BALANCE", "message": "Insufficient wallet balance"},
        )


# ─── Generic ───────────────────────────────────────────────────────────────────
class NotFoundException(HTTPException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"{resource} not found"},
        )


class ValidationException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "VALIDATION_ERROR", "message": detail},
        )


class ServiceUnavailableException(HTTPException):
    def __init__(self, service: str = "Service"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "SERVICE_UNAVAILABLE", "message": f"{service} is temporarily unavailable"},
        )
