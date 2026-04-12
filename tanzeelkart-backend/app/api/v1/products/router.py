from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.v1.products import schemas, service
from app.api.deps import get_current_user, get_current_shopkeeper
from app.models.user import User
from typing import Optional

router = APIRouter()


# ── Create Product ────────────────────────
@router.post("/", response_model=dict)
async def create_product(
    payload: schemas.CreateProductRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_shopkeeper),
):
    return await service.create_product(
        payload, db, current_user
    )


# ── My Products ───────────────────────────
@router.get("/my-products",
            response_model=schemas.ProductListResponse)
async def get_my_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_shopkeeper),
):
    return await service.get_my_products(
        db, current_user, page, per_page
    )


# ── Shop Products (Public) ────────────────
@router.get("/shop/{shop_id}",
            response_model=schemas.ProductListResponse)
async def get_shop_products(
    shop_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_shop_products(
        shop_id, db, page, per_page
    )


# ── Search Products ───────────────────────
@router.get("/search",
            response_model=schemas.ProductListResponse)
async def search_products(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await service.search_products(
        query, db, page, per_page
    )


# ── Update Stock ──────────────────────────
@router.patch("/{product_id}/stock")
async def update_stock(
    product_id: str,
    stock: int = Query(..., ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_shopkeeper),
):
    return await service.update_stock(
        product_id, stock, db, current_user
    )


# ── Update Product ────────────────────────
@router.put("/{product_id}",
            response_model=schemas.ProductResponse)
async def update_product(
    product_id: str,
    payload: schemas.UpdateProductRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_shopkeeper),
):
    return await service.update_product(
        product_id, payload, db, current_user
    )


# ── Delete Product ────────────────────────
@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_shopkeeper),
):
    return await service.delete_product(
        product_id, db, current_user
    )
