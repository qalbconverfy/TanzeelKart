from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.v1.orders import schemas, service
from app.api.deps import (
    get_current_user,
    get_current_shopkeeper
)
from app.models.user import User
from typing import Optional

router = APIRouter()


# ── Place Order ───────────────────────────
@router.post("/", response_model=dict)
async def create_order(
    payload: schemas.CreateOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.create_order(
        payload, db, current_user
    )


# ── My Orders (Buyer) ─────────────────────
@router.get("/my-orders")
async def get_my_orders(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.get_my_orders(
        db, current_user, page, per_page
    )


# ── Shop Orders (Shopkeeper) ──────────────
@router.get("/shop-orders")
async def get_shop_orders(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_shopkeeper),
):
    return await service.get_shop_orders(
        db, current_user, status, page, per_page
    )


# ── Update Order Status ───────────────────
@router.patch("/{order_id}/status")
async def update_order_status(
    order_id: str,
    payload: schemas.UpdateOrderStatusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_shopkeeper),
):
    return await service.update_order_status(
        order_id, payload, db, current_user
    )


# ── Cancel Order ──────────────────────────
@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: str,
    payload: schemas.CancelOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.cancel_order(
        order_id, payload, db, current_user
    )


# ── Order Detail ──────────────────────────
@router.get("/{order_id}",
            response_model=schemas.OrderResponse)
async def get_order_detail(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.get_order_detail(
        order_id, db, current_user
    )
