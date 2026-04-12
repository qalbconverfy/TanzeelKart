from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from app.models.notification import Notification
from app.models.user import User
from app.api.v1.notifications.schemas import (
    NotificationResponse,
    NotificationListResponse,
    MarkReadRequest
)
from app.core.exceptions import NotFoundException
from loguru import logger


# ─────────────────────────────────────────
# Get My Notifications
# ─────────────────────────────────────────

async def get_my_notifications(
    db: AsyncSession,
    current_user: User,
    page: int = 1,
    per_page: int = 20,
) -> NotificationListResponse:
    offset = (page - 1) * per_page

    # Total count
    count_result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == current_user.id,
            Notification.is_deleted == False
        )
    )
    total = count_result.scalar()

    # Unread count
    unread_result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == current_user.id,
            Notification.is_read == False,
            Notification.is_deleted == False
        )
    )
    unread_count = unread_result.scalar()

    # Notifications
    result = await db.execute(
        select(Notification).where(
            Notification.user_id == current_user.id,
            Notification.is_deleted == False
        ).order_by(
            Notification.created_at.desc()
        ).offset(offset).limit(per_page)
    )
    notifications = result.scalars().all()

    return NotificationListResponse(
        notifications=[
            NotificationResponse.model_validate(n)
            for n in notifications
        ],
        total=total,
        unread_count=unread_count
    )


# ─────────────────────────────────────────
# Mark As Read
# ─────────────────────────────────────────

async def mark_as_read(
    payload: MarkReadRequest,
    db: AsyncSession,
    current_user: User,
) -> dict:
    await db.execute(
        update(Notification).where(
            Notification.id.in_(payload.notification_ids),
            Notification.user_id == current_user.id
        ).values(is_read=True)
    )
    await db.commit()

    return {
        "success": True,
        "message": "Notifications marked as read"
    }


# ─────────────────────────────────────────
# Mark All As Read
# ─────────────────────────────────────────

async def mark_all_read(
    db: AsyncSession,
    current_user: User,
) -> dict:
    await db.execute(
        update(Notification).where(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        ).values(is_read=True)
    )
    await db.commit()

    return {
        "success": True,
        "message": "All notifications marked as read"
    }


# ─────────────────────────────────────────
# Delete Notification
# ─────────────────────────────────────────

async def delete_notification(
    notification_id: str,
    db: AsyncSession,
    current_user: User,
) -> dict:
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
            Notification.is_deleted == False
        )
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise NotFoundException("Notification not found")

    notification.is_deleted = True
    await db.commit()

    return {
        "success": True,
        "message": "Notification deleted"
    }
