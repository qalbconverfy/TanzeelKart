from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.v1.admin import schemas, service
from app.api.deps import get_current_admin
from app.models.user import User

router = APIRouter()


# ── Platform Stats ────────────────────────
@router.get("/stats",
            response_model=schemas.AdminStatsResponse)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return await service.get_platform_stats(db)


# ── Add Admin ─────────────────────────────
@router.post("/add-admin")
async def add_admin(
    payload: schemas.AddAdminRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return await service.add_admin(
        payload, db, current_admin
    )


# ── Pending Verifications ─────────────────
@router.get("/pending-verifications")
async def get_pending_verifications(
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return await service.get_pending_verifications(db)


# ── Verify Shop ───────────────────────────
@router.post("/verify-shop")
async def verify_shop(
    payload: schemas.VerifyShopRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return await service.verify_shop(payload, db)


# ── Verify Medical ────────────────────────
@router.post("/verify-medical")
async def verify_medical(
    payload: schemas.VerifyMedicalRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return await service.verify_medical(payload, db)


# ── All Users ─────────────────────────────
@router.get("/users")
async def get_all_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return await service.get_all_users(db, page, per_page)
