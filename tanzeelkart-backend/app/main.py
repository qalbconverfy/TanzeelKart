from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_fastapi_instrumentator import Instrumentator
import time

from app.core.config import settings
from app.core.database import init_db
from app.core.redis import init_redis, close_redis
from app.core.exceptions import TanzeelKartException
from app.api.v1.auth.router import router as auth_router
from app.api.v1.users.router import router as users_router
from app.api.v1.shops.router import router as shops_router
from app.api.v1.products.router import router as products_router
from app.api.v1.orders.router import router as orders_router
from app.api.v1.delivery.router import router as delivery_router
from app.api.v1.weather.router import router as weather_router
from app.api.v1.udhaar.router import router as udhaar_router
from app.api.v1.notifications.router import router as notifications_router
from app.api.v1.videos.router import router as videos_router
from app.api.v1.map.router import router as map_router
from app.api.v1.admin.router import router as admin_router


# Rate Limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 TanzeelKart Backend Starting...")
    await init_db()
    await init_redis()
    logger.info("✅ All services connected!")
    yield
    # Shutdown
    await close_redis()
    logger.info("👋 TanzeelKart Backend Stopped")


app = FastAPI(
    title="TanzeelKart API",
    description="TanzeelKart — Local Marketplace + Weather Platform by QalbConverfy",
    version=settings.APP_VERSION,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Prometheus Monitoring
Instrumentator().instrument(app).expose(app)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception Handlers
@app.exception_handler(TanzeelKartException)
async def tanzeelkart_exception_handler(
    request: Request,
    exc: TanzeelKartException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error",
            "errors": exc.errors()
        }
    )


# Routers
app.include_router(
    auth_router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Authentication"]
)
app.include_router(
    products_router,
    prefix=f"{settings.API_V1_PREFIX}/products",
    tags=["Products"]
)
app.include_router(
    users_router,
    prefix=f"{settings.API_V1_PREFIX}/users",
    tags=["Users"]
)
app.include_router(
    shops_router,
    prefix=f"{settings.API_V1_PREFIX}/shops",
    tags=["Shops"]
)
app.include_router(
    orders_router,
    prefix=f"{settings.API_V1_PREFIX}/orders",
    tags=["Orders"]
)
app.include_router(
    delivery_router,
    prefix=f"{settings.API_V1_PREFIX}/delivery",
    tags=["Delivery"]
)
app.include_router(
    weather_router,
    prefix=f"{settings.API_V1_PREFIX}/weather",
    tags=["Weather"]
)
app.include_router(
    udhaar_router,
    prefix=f"{settings.API_V1_PREFIX}/udhaar",
    tags=["Udhaar"]
)
app.include_router(
    notifications_router,
    prefix=f"{settings.API_V1_PREFIX}/notifications",
    tags=["Notifications"]
)
app.include_router(
    videos_router,
    prefix=f"{settings.API_V1_PREFIX}/videos",
    tags=["Videos"]
)
app.include_router(
    map_router,
    prefix=f"{settings.API_V1_PREFIX}/map",
    tags=["Map"]
)
app.include_router(
    admin_router,
    prefix=f"{settings.API_V1_PREFIX}/admin",
    tags=["Admin"]
)


# Health Check
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "success": True,
        "message": "TanzeelKart API is running!",
        "version": settings.APP_VERSION,
        "platform": "TanzeelKart by QalbConverfy"
    }
    
