from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from jose import JWTError
import logging
import time

from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.redis import init_redis, close_redis
from app.core.responses import error_response

# ─── Logger ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ─── Lifespan (startup + shutdown) ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"   Environment : {settings.ENVIRONMENT}")

    await init_db()
    await init_redis()

    logger.info("✅ All systems ready")
    yield

    # ── Shutdown ──
    logger.info("🛑 Shutting down...")
    await close_db()
    await close_redis()
    logger.info("Shutdown complete")


# ─── App Instance ──────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="TanzeelKart Backend API — Apna Gaon, Apna Bazaar",
    docs_url="/docs" if settings.DEBUG else None,      # hide Swagger in production
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)


# ─── CORS Middleware ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request Timing Middleware ─────────────────────────────────────────────────
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    response.headers["X-Process-Time"] = f"{duration:.4f}s"
    return response


# ─── Global Exception Handlers ────────────────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Pydantic validation errors — return structured 422."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " → ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation failed",
            "code": "VALIDATION_ERROR",
            "details": errors,
        },
    )


@app.exception_handler(JWTError)
async def jwt_exception_handler(request: Request, exc: JWTError):
    return JSONResponse(
        status_code=401,
        content={
            "success": False,
            "message": "Invalid or expired token",
            "code": "TOKEN_INVALID",
        },
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception on {request.method} {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An unexpected error occurred",
            "code": "INTERNAL_SERVER_ERROR",
        },
    )


# ─── Health Check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Public health check endpoint.
    Used by Render.com to verify the service is live.
    """
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "TanzeelKart API — Apna Gaon, Apna Bazaar",
        "docs": "/docs" if settings.DEBUG else "Disabled in production",
        "version": settings.APP_VERSION,
    }


# ─── API Routers ──────────────────────────────────────────────────────────────
# Routers will be imported and included here as each API module is built.
# Example (uncomment as you build each module):
#
# from app.api.v1.auth import router as auth_router
# from app.api.v1.users import router as users_router
# from app.api.v1.shops import router as shops_router
#
# app.include_router(auth_router,  prefix=settings.API_V1_PREFIX + "/auth",  tags=["Auth"])
# app.include_router(users_router, prefix=settings.API_V1_PREFIX + "/users", tags=["Users"])
# app.include_router(shops_router, prefix=settings.API_V1_PREFIX + "/shops", tags=["Shops"])
