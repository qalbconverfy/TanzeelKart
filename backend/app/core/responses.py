from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi import status

T = TypeVar("T")


# ─── Response Schemas ──────────────────────────────────────────────────────────
class APIResponse(BaseModel, Generic[T]):
    """Standard API response envelope used across all endpoints."""
    success: bool
    message: str
    data: Optional[T] = None
    code: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Response envelope for paginated list endpoints."""
    success: bool
    message: str
    data: list[T]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool


# ─── Success Helpers ───────────────────────────────────────────────────────────
def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = status.HTTP_200_OK,
    code: Optional[str] = None,
) -> JSONResponse:
    """Return a standardized success response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "message": message,
            "data": data,
            "code": code,
        },
    )


def created_response(
    data: Any = None,
    message: str = "Created successfully",
) -> JSONResponse:
    return success_response(data=data, message=message, status_code=status.HTTP_201_CREATED)


def paginated_response(
    data: list,
    total: int,
    page: int,
    per_page: int,
    message: str = "Success",
) -> JSONResponse:
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": message,
            "data": data,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
    )


# ─── Error Helper ──────────────────────────────────────────────────────────────
def error_response(
    message: str,
    code: str = "ERROR",
    status_code: int = status.HTTP_400_BAD_REQUEST,
    details: Any = None,
) -> JSONResponse:
    """Return a standardized error response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "code": code,
            "details": details,
        },
    )
