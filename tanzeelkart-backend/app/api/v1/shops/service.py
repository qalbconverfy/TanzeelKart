from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.shop import Shop, ShopStatus, ShopCategory
from app.models.user import User, UserRole
from app.models.verification import Verification, VerificationType
from app.api.v1.shops.schemas import (
    CreateShopRequest, UpdateShopRequest,
    ShopResponse, NearbyShopsRequest
)
from app.core.exceptions import (
    NotFoundException, PermissionException,
    ValidationException, DuplicateException
)
from app.utils.shop_id_generator import generate_shop_id
from loguru import logger
import math
import uuid


# ─────────────────────────────────────────
# Distance Calculator
# ─────────────────────────────────────────

def calculate_distance(
    lat1: float, lon1: float,
    lat2: float, lon2: float
) -> float:
    R = 6371  # Earth radius km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat/2) ** 2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(dlon/2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


# ─────────────────────────────────────────
# Create Shop
# ─────────────────────────────────────────

async def create_shop(
    payload: CreateShopRequest,
    db: AsyncSession,
    current_user: User,
) -> dict:
    # Check already has shop
    result = await db.execute(
        select(Shop).where(
            Shop.owner_id == current_user.id,
            Shop.is_deleted == False
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise DuplicateException("Shop already registered")

    # Check verified hai
    if not current_user.is_verified:
        raise PermissionException(
            "Complete shop verification first"
        )

    # Shop ID generate karo
    shop_id_code = await generate_shop_id(db)

    shop = Shop(
        id=uuid.uuid4(),
        name=payload.name,
        description=payload.description,
        owner_id=current_user.id,
        category=ShopCategory(payload.category),
        status=ShopStatus.PENDING,
        phone=payload.phone,
        whatsapp=payload.whatsapp,
        address=payload.address,
        village=payload.village,
        block="Reoti",
        district="Ballia",
        latitude=payload.latitude,
        longitude=payload.longitude,
        opening_time=payload.opening_time,
        closing_time=payload.closing_time,
        is_open_sunday=payload.is_open_sunday,
        delivery_radius_km=payload.delivery_radius_km,
        min_order_amount=payload.min_order_amount,
        delivery_charge=payload.delivery_charge,
        is_delivery_available=True,
    )

    db.add(shop)

    # User role update
    current_user.role = UserRole.SHOPKEEPER
    await db.commit()
    await db.refresh(shop)

    logger.info(f"Shop created: {shop.name} — {shop_id_code}")

    return {
        "success": True,
        "message": "Shop registered! Pending admin approval.",
        "shop_id": shop_id_code,
        "shop": ShopResponse.model_validate(shop)
    }


# ─────────────────────────────────────────
# Get My Shop
# ─────────────────────────────────────────

async def get_my_shop(
    db: AsyncSession,
    current_user: User,
) -> ShopResponse:
    result = await db.execute(
        select(Shop).where(
            Shop.owner_id == current_user.id,
            Shop.is_deleted == False
        )
    )
    shop = result.scalar_one_or_none()
    if not shop:
        raise NotFoundException("Shop not found")
    return ShopResponse.model_validate(shop)


# ─────────────────────────────────────────
# Update Shop
# ─────────────────────────────────────────

async def update_shop(
    payload: UpdateShopRequest,
    db: AsyncSession,
    current_user: User,
) -> ShopResponse:
    result = await db.execute(
        select(Shop).where(
            Shop.owner_id == current_user.id,
            Shop.is_deleted == False
        )
    )
    shop = result.scalar_one_or_none()
    if not shop:
        raise NotFoundException("Shop not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(shop, key, value)

    await db.commit()
    await db.refresh(shop)
    logger.info(f"Shop updated: {shop.name}")
    return ShopResponse.model_validate(shop)


# ─────────────────────────────────────────
# Nearby Shops
# ─────────────────────────────────────────

async def get_nearby_shops(
    payload: NearbyShopsRequest,
    db: AsyncSession,
) -> list:
    query = select(Shop).where(
        Shop.is_active == True,
        Shop.is_deleted == False,
        Shop.status == ShopStatus.VERIFIED,
    )

    if payload.category:
        query = query.where(
            Shop.category == ShopCategory(payload.category)
        )

    result = await db.execute(query)
    all_shops = result.scalars().all()

    # Distance filter
    nearby = []
    for shop in all_shops:
        distance = calculate_distance(
            payload.latitude, payload.longitude,
            shop.latitude, shop.longitude
        )
        if distance <= payload.radius_km:
            shop_dict = ShopResponse.model_validate(shop).model_dump()
            shop_dict["distance_km"] = round(distance, 2)
            nearby.append(shop_dict)

    # Sort by distance
    nearby.sort(key=lambda x: x["distance_km"])
    return nearby


# ─────────────────────────────────────────
# Search Shops
# ─────────────────────────────────────────

async def search_shops(
    query: str,
    db: AsyncSession,
    category: str = None,
) -> list:
    stmt = select(Shop).where(
        Shop.is_active == True,
        Shop.is_deleted == False,
        Shop.status == ShopStatus.VERIFIED,
        Shop.name.ilike(f"%{query}%")
    )

    if category:
        stmt = stmt.where(
            Shop.category == ShopCategory(category)
        )

    result = await db.execute(stmt)
    shops = result.scalars().all()
    return [ShopResponse.model_validate(s) for s in shops]


# ─────────────────────────────────────────
# Get Shop By ID
# ─────────────────────────────────────────

async def get_shop_by_id(
    shop_id: str,
    db: AsyncSession,
) -> ShopResponse:
    result = await db.execute(
        select(Shop).where(
            Shop.id == shop_id,
            Shop.is_deleted == False
        )
    )
    shop = result.scalar_one_or_none()
    if not shop:
        raise NotFoundException("Shop not found")
    return ShopResponse.model_validate(shop)


# ─────────────────────────────────────────
# Get Shop By TK Code
# ─────────────────────────────────────────

async def get_shop_by_tk_code(
    tk_code: str,
    db: AsyncSession,
) -> dict:
    # Verification table se dhundo
    from app.models.verification import Verification
    result = await db.execute(
        select(Verification).where(
            Verification.shop_id == tk_code,
            Verification.is_verified == True
        )
    )
    verification = result.scalar_one_or_none()
    if not verification:
        raise NotFoundException("Shop ID not found")

    # Shop details lo
    shop_result = await db.execute(
        select(Shop).where(
            Shop.owner_id == verification.user_id,
            Shop.is_deleted == False
        )
    )
    shop = shop_result.scalar_one_or_none()
    if not shop:
        raise NotFoundException("Shop not found")

    return {
        "success": True,
        "tk_code": tk_code,
        "owner_name": verification.shop_owner_name,
        "seller_name": verification.seller_name,
        "shop": ShopResponse.model_validate(shop)
    }
