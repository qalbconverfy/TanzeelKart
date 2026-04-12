from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.v1.udhaar import schemas, service
from app.api.deps import (
    get_current_user,
    get_current_shopkeeper
)
from app.models.user import User

router = APIRouter()


# ── Add Udhaar ────────────────────────────
@router.post("/add")
async def add_udhaar(
    payload: schemas.AddUdhaarRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.add_udhaar(
        payload, db, current_user
    )


# ── Pay Udhaar ────────────────────────────
@router.post("/pay")
async def pay_udhaar(
    payload: schemas.PayUdhaarRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.pay_udhaar(
        payload, db, current_user
    )


# ── My Udhaar ─────────────────────────────
@router.get("/my-udhaar",
            response_model=schemas.UdhaarSummaryResponse)
async def get_my_udhaar(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.get_my_udhaar(db, current_user)


# ── Delivery Charge Account ───────────────
@router.get("/delivery-charges",
            response_model=schemas.DeliveryChargeResponse)
async def get_delivery_charges(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.get_delivery_charge_account(
        db, current_user
    )


# ── Pay Delivery Charge ───────────────────
@router.post("/pay-delivery-charge")
async def pay_delivery_charge(
    payload: schemas.PayDeliveryChargeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.pay_delivery_charge(
        payload, db, current_user
    )


# ── Shop Udhaar List ──────────────────────
@router.get("/shop-list")
async def get_shop_udhaar_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_shopkeeper),
):
    return await service.get_shop_udhaar_list(
        db, current_user
    )
