from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.v1.map import schemas, service
from typing import Optional

router = APIRouter()


# ── Full Map Data ─────────────────────────
@router.get("/data",
            response_model=schemas.MapDataResponse)
async def get_map_data(
    latitude: float = Query(26.0500),
    longitude: float = Query(84.1800),
    radius_km: float = Query(2.0),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_map_data(
        db, latitude, longitude, radius_km
    )


# ── Shops On Map ──────────────────────────
@router.get("/shops")
async def get_shops_on_map(
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_shops_on_map(db, category)


# ── Landmarks ─────────────────────────────
@router.get("/landmarks")
async def get_landmarks():
    return service.REOTI_LANDMARKS
