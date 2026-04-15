from typing import Any, Optional, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    errors: Optional[Any] = None


def success(
    message: str,
    data: Any = None,
) -> dict:
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error(
    message: str,
    errors: Any = None,
) -> dict:
    return {
        "success": False,
        "message": message,
        "errors": errors,
    }
