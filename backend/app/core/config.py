from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # ─── App ───────────────────────────────────────────────────────────────────
    APP_NAME: str = "TanzeelKart API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"  # development | production
    API_V1_PREFIX: str = "/api/v1"

    # ─── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str  # postgresql+asyncpg://user:pass@host/db
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30

    # ─── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: str  # redis://default:pass@host:port

    # ─── JWT ───────────────────────────────────────────────────────────────────
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60          # 1 hour
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ─── OTP ───────────────────────────────────────────────────────────────────
    OTP_EXPIRE_SECONDS: int = 600                  # 10 minutes
    OTP_RESEND_SECONDS: int = 30
    OTP_LENGTH: int = 6

    # ─── Fast2SMS ──────────────────────────────────────────────────────────────
    FAST2SMS_API_KEY: str

    # ─── Cloudinary ────────────────────────────────────────────────────────────
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    # ─── YouTube ───────────────────────────────────────────────────────────────
    YOUTUBE_API_KEY: str

    # ─── Email (SMTP) ──────────────────────────────────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@qalbconverfy.in"

    # ─── CORS ──────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: List[str] = [
        "https://tk.qalbconverfy.in",
        "https://qalbconverfy.in",
        "http://localhost:3000",
    ]

    # ─── Platform ──────────────────────────────────────────────────────────────
    MAX_DELIVERY_RADIUS_KM: float = 2.0
    DELIVERY_CHARGE_THRESHOLD: float = 50.0        # orders below this → accumulate
    SUNDAY_COLLECTION_DAY: int = 6                 # 0=Mon … 6=Sun
    SHOP_ID_PREFIX: str = "TK"
    SHOP_ID_YEAR: int = 2026

    # ─── Rate Limiting ─────────────────────────────────────────────────────────
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_OTP: str = "5/minute"
    RATE_LIMIT_LOGIN: str = "10/minute"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
