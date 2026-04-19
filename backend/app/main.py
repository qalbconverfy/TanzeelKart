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
from app.core.exceptions import AppException
from app.api.v1.auth.router import router as auth_router


# ── Rate Limiter ──────────────────────────
limiter = Limiter(key_func=get_remote_address)


# ── Lifespan ─────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 TanzeelKart Starting...")
    await init_db()
    await init_redis()
    logger.info("✅ All services connected!")
    yield
    await close_redis()
    logger.info("👋 TanzeelKart Stopped")


# ── App ───────────────────────────────────
app = FastAPI(
    title="TanzeelKart API",
    description=(
        "TanzeelKart — Local Marketplace + "
        "Weather Platform by QalbConverfy (ZEAIPC)"
    ),
    version=settings.APP_VERSION,
    docs_url=(
        f"{settings.API_V1_PREFIX}/docs"
        if settings.DEBUG else None
    ),
    redoc_url=(
        f"{settings.API_V1_PREFIX}/redoc"
        if settings.DEBUG else None
    ),
    lifespan=lifespan,
)

# ── Rate Limiter ──────────────────────────
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

# ── Prometheus ────────────────────────────
Instrumentator().instrument(app).expose(app)

# ── CORS ─────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Trusted Hosts ─────────────────────────
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],
)


# ── Request Timing ────────────────────────
@app.middleware("http")
async def add_process_time(
    request: Request, call_next
):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = (
        str(time.time() - start)
    )
    return response


# ── Exception Handlers ────────────────────
@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request, exc: AppException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error",
            "errors": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request, exc: Exception
):
    logger.error(f"Unhandled: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Server error",
        },
    )


# ── Routers ───────────────────────────────
app.include_router(
    auth_router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Authentication"],
)


# ── Health ────────────────────────────────
@app.get("/health", tags=["Health"])
async def health():
    return {
        "success": True,
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "company": "QalbConverfy (ZEAIPC)",
        "location": "Reoti, Ballia, UP",
    }
