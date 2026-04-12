from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.v1.shops import schemas, service
from app.api.deps import get_current_user, get_current_shopkeeper
from app.models.user import User
from typing import Optional

router = APIRouter()


# ── Create Shop ───────────────────────────
@router.post("/", response_model=dict)
async def create_shop(
    payload: schemas.CreateShopRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.create_shop(payload, db, current_user)


# ── My Shop ───────────────────────────────
@router.get("/my-shop", response_model=schemas.ShopResponse)
async def get_my_shop(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_shopkeeper),
):
    return await service.get_my_shop(db, current_user)


# ── Update Shop ───────────────────────────
@router.put("/my-shop", response_model=schemas.ShopResponse)
async def update_shop(
    payload: schemas.UpdateShopRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_shopkeeper),
):
    return await service.update_shop(payload, db, current_user)


# ── Nearby Shops ──────────────────────────
@router.post("/nearby", response_model=list)
async def get_nearby_shops(
    payload: schemas.NearbyShopsRequest,
    db: AsyncSession = Depends(get_db),
):
    return await service.get_nearby_shops(payload, db)


# ── Search Shops ──────────────────────────
@router.get("/search", response_model=list)
async def search_shops(
    query: str = Query(..., min_length=1),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await service.search_shops(query, db, category)


# ── Shop By TK Code ───────────────────────
@router.get("/tk/{tk_code}")
async def get_shop_by_tk_code(
    tk_code: str,
    db: AsyncSession = Depends(get_db),
):
    return await service.get_shop_by_tk_code(tk_code, db)


# ── Shop By ID ────────────────────────────
@router.get("/{shop_id}", response_model=schemas.ShopResponse)
async def get_shop_by_id(
    shop_id: str,
    db: AsyncSession = Depends(get_db),
):
    return await service.get_shop_by_id(shop_id, db)
