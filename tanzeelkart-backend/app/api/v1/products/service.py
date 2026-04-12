from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.product import Product, ProductStatus
from app.models.shop import Shop, ShopStatus
from app.models.user import User
from app.api.v1.products.schemas import (
    CreateProductRequest,
    UpdateProductRequest,
    ProductResponse,
    ProductListResponse
)
from app.core.exceptions import (
    NotFoundException,
    PermissionException,
    ValidationException
)
from loguru import logger
import uuid


# ─────────────────────────────────────────
# Create Product
# ─────────────────────────────────────────

async def create_product(
    payload: CreateProductRequest,
    db: AsyncSession,
    current_user: User,
) -> dict:
    # Shop dhundo
    shop_result = await db.execute(
        select(Shop).where(
            Shop.owner_id == current_user.id,
            Shop.is_deleted == False
        )
    )
    shop = shop_result.scalar_one_or_none()
    if not shop:
        raise NotFoundException("Shop not found. Register shop first.")

    if shop.status != ShopStatus.VERIFIED:
        raise PermissionException(
            "Shop not verified yet. Wait for admin approval."
        )

    product = Product(
        id=uuid.uuid4(),
        name=payload.name,
        description=payload.description,
        shop_id=shop.id,
        price=payload.price,
        discount_price=payload.discount_price,
        unit=payload.unit,
        stock=payload.stock,
        min_order_qty=payload.min_order_qty,
        max_order_qty=payload.max_order_qty,
        tags=payload.tags,
        status=ProductStatus.ACTIVE,
    )

    db.add(product)
    await db.commit()
    await db.refresh(product)
    logger.info(f"Product created: {product.name}")

    return {
        "success": True,
        "message": "Product added successfully!",
        "product": ProductResponse.model_validate(product)
    }


# ─────────────────────────────────────────
# Get My Products
# ─────────────────────────────────────────

async def get_my_products(
    db: AsyncSession,
    current_user: User,
    page: int = 1,
    per_page: int = 20,
) -> ProductListResponse:
    shop_result = await db.execute(
        select(Shop).where(
            Shop.owner_id == current_user.id,
            Shop.is_deleted == False
        )
    )
    shop = shop_result.scalar_one_or_none()
    if not shop:
        raise NotFoundException("Shop not found")

    offset = (page - 1) * per_page

    # Total count
    count_result = await db.execute(
        select(func.count(Product.id)).where(
            Product.shop_id == shop.id,
            Product.is_deleted == False
        )
    )
    total = count_result.scalar()

    # Products
    result = await db.execute(
        select(Product).where(
            Product.shop_id == shop.id,
            Product.is_deleted == False
        ).offset(offset).limit(per_page)
    )
    products = result.scalars().all()

    return ProductListResponse(
        products=[
            ProductResponse.model_validate(p)
            for p in products
        ],
        total=total,
        page=page,
        per_page=per_page
    )


# ─────────────────────────────────────────
# Get Shop Products (Public)
# ─────────────────────────────────────────

async def get_shop_products(
    shop_id: str,
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    category: str = None,
) -> ProductListResponse:
    offset = (page - 1) * per_page

    query = select(Product).where(
        Product.shop_id == shop_id,
        Product.is_deleted == False,
        Product.is_active == True,
        Product.status == ProductStatus.ACTIVE,
    )

    count_query = select(func.count(Product.id)).where(
        Product.shop_id == shop_id,
        Product.is_deleted == False,
        Product.is_active == True,
    )

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    result = await db.execute(
        query.offset(offset).limit(per_page)
    )
    products = result.scalars().all()

    return ProductListResponse(
        products=[
            ProductResponse.model_validate(p)
            for p in products
        ],
        total=total,
        page=page,
        per_page=per_page
    )


# ─────────────────────────────────────────
# Update Product
# ─────────────────────────────────────────

async def update_product(
    product_id: str,
    payload: UpdateProductRequest,
    db: AsyncSession,
    current_user: User,
) -> ProductResponse:
    # Shop check
    shop_result = await db.execute(
        select(Shop).where(
            Shop.owner_id == current_user.id,
            Shop.is_deleted == False
        )
    )
    shop = shop_result.scalar_one_or_none()
    if not shop:
        raise NotFoundException("Shop not found")

    # Product check
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.shop_id == shop.id,
            Product.is_deleted == False
        )
    )
    product = result.scalar_one_or_none()
    if not product:
        raise NotFoundException("Product not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    await db.commit()
    await db.refresh(product)
    logger.info(f"Product updated: {product.name}")
    return ProductResponse.model_validate(product)


# ─────────────────────────────────────────
# Delete Product
# ─────────────────────────────────────────

async def delete_product(
    product_id: str,
    db: AsyncSession,
    current_user: User,
) -> dict:
    shop_result = await db.execute(
        select(Shop).where(
            Shop.owner_id == current_user.id,
            Shop.is_deleted == False
        )
    )
    shop = shop_result.scalar_one_or_none()
    if not shop:
        raise NotFoundException("Shop not found")

    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.shop_id == shop.id,
            Product.is_deleted == False
        )
    )
    product = result.scalar_one_or_none()
    if not product:
        raise NotFoundException("Product not found")

    product.is_deleted = True
    product.is_active = False
    await db.commit()

    logger.info(f"Product deleted: {product.name}")
    return {
        "success": True,
        "message": "Product deleted successfully"
    }


# ─────────────────────────────────────────
# Search Products
# ─────────────────────────────────────────

async def search_products(
    query: str,
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
) -> ProductListResponse:
    offset = (page - 1) * per_page

    stmt = select(Product).where(
        Product.is_deleted == False,
        Product.is_active == True,
        Product.status == ProductStatus.ACTIVE,
        Product.name.ilike(f"%{query}%")
    )

    count_result = await db.execute(
        select(func.count(Product.id)).where(
            Product.is_deleted == False,
            Product.is_active == True,
            Product.name.ilike(f"%{query}%")
        )
    )
    total = count_result.scalar()

    result = await db.execute(
        stmt.offset(offset).limit(per_page)
    )
    products = result.scalars().all()

    return ProductListResponse(
        products=[
            ProductResponse.model_validate(p)
            for p in products
        ],
        total=total,
        page=page,
        per_page=per_page
    )


# ─────────────────────────────────────────
# Update Stock
# ─────────────────────────────────────────

async def update_stock(
    product_id: str,
    stock: int,
    db: AsyncSession,
    current_user: User,
) -> dict:
    shop_result = await db.execute(
        select(Shop).where(
            Shop.owner_id == current_user.id,
            Shop.is_deleted == False
        )
    )
    shop = shop_result.scalar_one_or_none()
    if not shop:
        raise NotFoundException("Shop not found")

    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.shop_id == shop.id,
            Product.is_deleted == False
        )
    )
    product = result.scalar_one_or_none()
    if not product:
        raise NotFoundException("Product not found")

    if stock < 0:
        raise ValidationException("Stock cannot be negative")

    old_stock = product.stock
    product.stock = stock

    if stock == 0:
        product.status = ProductStatus.OUT_OF_STOCK
    else:
        product.status = ProductStatus.ACTIVE

    await db.commit()
    logger.info(
        f"Stock updated: {product.name} "
        f"{old_stock} → {stock}"
    )

    return {
        "success": True,
        "message": "Stock updated",
        "product_name": product.name,
        "old_stock": old_stock,
        "new_stock": stock
    }
