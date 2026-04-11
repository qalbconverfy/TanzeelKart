from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.v1.users import schemas, service
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/me", response_model=schemas.UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return schemas.UserResponse.model_validate(current_user)


@router.put("/me", response_model=schemas.UserResponse)
async def update_my_profile(
    payload: schemas.UpdateUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.update_profile(payload, db, current_user)


@router.get("/me/finance", response_model=schemas.UserFinanceResponse)
async def get_my_finance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.get_finance_summary(db, current_user)


@router.put("/me/fcm-token")
async def update_fcm_token(
    payload: schemas.FCMTokenRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.update_fcm_token(payload, db, current_user)
    