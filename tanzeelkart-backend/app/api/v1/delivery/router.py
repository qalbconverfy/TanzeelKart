from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.v1.delivery import schemas, service
from app.api.deps import (
    get_current_user,
    get_current_delivery_boy
)
from app.models.user import User
from typing import Optional

router = APIRouter()


# ── Pending Deliveries ────────────────────
@router.get("/pending")
async def get_pending_deliveries(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_delivery_boy),
):
    return await service.get_pending_deliveries(
        db, current_user
    )


# ── Assign Delivery ───────────────────────
@router.post("/assign")
async def assign_delivery(
    payload: schemas.AssignDeliveryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_delivery_boy),
):
    return await service.assign_delivery(
        payload, db, current_user
    )


# ── Update Status ─────────────────────────
@router.patch("/{delivery_id}/status")
async def update_delivery_status(
    delivery_id: str,
    payload: schemas.UpdateDeliveryStatusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_delivery_boy),
):
    return await service.update_delivery_status(
        delivery_id, payload, db, current_user
    )


# ── Update Location ───────────────────────
@router.patch("/{delivery_id}/location")
async def update_location(
    delivery_id: str,
    payload: schemas.UpdateLocationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_delivery_boy),
):
    return await service.update_live_location(
        delivery_id, payload, db, current_user
    )


# ── My Deliveries ─────────────────────────
@router.get("/my-deliveries")
async def get_my_deliveries(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_delivery_boy),
):
    return await service.get_my_deliveries(
        db, current_user, status, page, per_page
    )


# ── Sunday Collection List ────────────────
@router.get("/sunday-collection-list")
async def get_sunday_collection_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.get_sunday_collection_list(
        db, current_user
    )


# ── Sunday Collection ─────────────────────
@router.post("/sunday-collection")
async def sunday_collection(
    payload: schemas.SundayCollectionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.sunday_collection(
        payload, db, current_user
    )
