from fastapi import APIRouter, Depends, Query
from app.api.v1.videos import schemas, service
from typing import Optional

router = APIRouter()


# ── Get Categories ────────────────────────
@router.get("/categories")
async def get_categories():
    return await service.get_categories()


# ── Trending Videos ───────────────────────
@router.get("/trending")
async def get_trending():
    return await service.get_trending_videos()


# ── Videos By Category ───────────────────
@router.get("/category/{category_name}")
async def get_by_category(
    category_name: str,
    max_results: int = Query(10, ge=1, le=50),
):
    return await service.get_videos_by_category(
        category_name, max_results
    )


# ── Search Videos ─────────────────────────
@router.post("/search",
             response_model=schemas.VideoListResponse)
async def search_videos(
    payload: schemas.VideoSearchRequest,
):
    return await service.search_videos(payload)
