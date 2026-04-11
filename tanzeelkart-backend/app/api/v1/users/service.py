from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.udhaar import DeliveryChargeAccount
from app.api.v1.users.schemas import (
    UpdateUserRequest, UserResponse,
    UserFinanceResponse, FCMTokenRequest
)
from app.core.exceptions import NotFoundException
from loguru import logger


async def update_profile(
    payload: UpdateUserRequest,
    db: AsyncSession,
    current_user: User,
) -> UserResponse:
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)

    await db.commit()
    await db.refresh(current_user)
    logger.info(f"Profile updated: {current_user.id}")
    return UserResponse.model_validate(current_user)


async def get_finance_summary(
    db: AsyncSession,
    current_user: User,
) -> UserFinanceResponse:
    result = await db.execute(
        select(DeliveryChargeAccount).where(
            DeliveryChargeAccount.user_id == current_user.id
        )
    )
    charge_account = result.scalar_one_or_none()

    return UserFinanceResponse(
        total_delivery_charges_pending=current_user.total_delivery_charges_pending,
        total_udhaar_pending=current_user.total_udhaar_pending,
        accumulated_delivery_charges=current_user.accumulated_delivery_charges,
        discount_percentage=current_user.discount_percentage,
        is_sunday_collection_pending=charge_account.is_sunday_pending if charge_account else False,
    )


async def update_fcm_token(
    payload: FCMTokenRequest,
    db: AsyncSession,
    current_user: User,
) -> dict:
    current_user.fcm_token = payload.fcm_token
    await db.commit()
    return {"success": True, "message": "FCM token updated"}
    