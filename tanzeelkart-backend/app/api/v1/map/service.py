from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.shop import Shop, ShopStatus
from app.api.v1.map.schemas import MapDataResponse
from loguru import logger


# Reoti Block Center
REOTI_CENTER_LAT = 26.0500
REOTI_CENTER_LON = 84.1800

# Landmarks
REOTI_LANDMARKS = [
    {
        "id": "lm_001",
        "name": "Reoti Bazaar",
        "latitude": 26.0500,
        "longitude": 84.1800,
        "category": "bazaar",
        "description": "Main market area"
    },
    {
        "id": "lm_002",
        "name": "Reoti Block Office",
        "latitude": 26.0510,
        "longitude": 84.1810,
        "category": "government",
        "description": "Block office"
    },
    {
        "id": "lm_003",
        "name": "Primary Health Center",
        "latitude": 26.0490,
        "longitude": 84.1790,
        "category": "medical",
        "description": "PHC Reoti"
    },
]


# ─────────────────────────────────────────
# Get Full Map Data
# ─────────────────────────────────────────

async def get_map_data(
    db: AsyncSession,
    latitude: float = REOTI_CENTER_LAT,
    longitude: float = REOTI_CENTER_LON,
    radius_km: float = 2.0,
) -> MapDataResponse:
    # Shops fetch karo
    result = await db.execute(
        select(Shop).where(
            Shop.is_active == True,
            Shop.is_deleted == False,
            Shop.status == ShopStatus.VERIFIED
        )
    )
    shops = result.scalars().all()

    shop_list = []
    for shop in shops:
        shop_list.append({
            "id": str(shop.id),
            "name": shop.name,
            "latitude": shop.latitude,
            "longitude": shop.longitude,
            "category": shop.category.value,
            "phone": shop.phone,
            "is_delivery": shop.is_delivery_available,
            "rating": shop.rating,
            "opening_time": shop.opening_time,
            "closing_time": shop.closing_time,
        })

    # Weather nodes
    weather_nodes = [
        {
            "id": "reoti_main",
            "name": "Reoti Bazaar Sensor",
            "latitude": 26.0500,
            "longitude": 84.1800,
            "is_active": True,
        },
        {
            "id": "reoti_khet",
            "name": "Khet Area Sensor",
            "latitude": 26.0450,
            "longitude": 84.1750,
            "is_active": True,
        },
    ]

    return MapDataResponse(
        shops=shop_list,
        weather_nodes=weather_nodes,
        landmarks=REOTI_LANDMARKS,
        center_latitude=REOTI_CENTER_LAT,
        center_longitude=REOTI_CENTER_LON,
        zoom_level=14
    )


# ─────────────────────────────────────────
# Get Shops On Map
# ─────────────────────────────────────────

async def get_shops_on_map(
    db: AsyncSession,
    category: str = None,
) -> list:
    query = select(Shop).where(
        Shop.is_active == True,
        Shop.is_deleted == False,
        Shop.status == ShopStatus.VERIFIED
    )

    if category:
        from app.models.shop import ShopCategory
        query = query.where(
            Shop.category == ShopCategory(category)
        )

    result = await db.execute(query)
    shops = result.scalars().all()

    return [
        {
            "id": str(s.id),
            "name": s.name,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "category": s.category.value,
            "phone": s.phone,
            "rating": s.rating,
        }
        for s in shops
    ]
