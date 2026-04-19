from fastapi import HTTPException, status
from typing import Optional


class AppException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[dict] = None,
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers,
        )


class AuthException(AppException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(AppException):
    def __init__(self, detail: str = "Access denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class NotFoundException(AppException):
    def __init__(self, detail: str = "Not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class ConflictException(AppException):
    def __init__(self, detail: str = "Already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class ValidationException(AppException):
    def __init__(self, detail: str = "Validation failed"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class PaymentException(AppException):
    def __init__(self, detail: str = "Payment failed"):
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=detail,
        )
