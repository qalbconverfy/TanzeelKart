from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.v1.notifications import schemas, service
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


# ── Get Notifications ─────────────────────
@router.get("/",
            response_model=schemas.NotificationListResponse)
async def get_notifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.get_my_notifications(
        db, current_user, page, per_page
    )


# ── Mark Read ─────────────────────────────
@router.patch("/mark-read")
async def mark_as_read(
    payload: schemas.MarkReadRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.mark_as_read(
        payload, db, current_user
    )


# ── Mark All Read ─────────────────────────
@router.patch("/mark-all-read")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.mark_all_read(db, current_user)


# ── Delete Notification ───────────────────
@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.delete_notification(
        notification_id, db, current_user
    )
