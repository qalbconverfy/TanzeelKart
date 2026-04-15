from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
from functools import lru_cache


class Settings(BaseSettings):

    # ── App ──────────────────────────────
    APP_NAME: str = "TanzeelKart"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str
    ALLOWED_HOSTS: List[str] = ["*"]
    API_V1_PREFIX: str = "/api/v1"

    # ── Database ─────────────────────────
    DATABASE_URL: str
    SYNC_DATABASE_URL: str

    # ── Redis ────────────────────────────
    REDIS_URL: str

    # ── InfluxDB ─────────────────────────
    INFLUXDB_URL: str = "http://localhost:8086"
    INFLUXDB_TOKEN: str = "placeholder"
    INFLUXDB_ORG: str = "tanzeelkart"
    INFLUXDB_BUCKET: str = "sensor_data"

    # ── Cloudinary ───────────────────────
    CLOUDINARY_CLOUD_NAME: str = "placeholder"
    CLOUDINARY_API_KEY: str = "placeholder"
    CLOUDINARY_API_SECRET: str = "placeholder"

    # ── JWT ──────────────────────────────
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── OTP ──────────────────────────────
    OTP_EXPIRE_SECONDS: int = 600

    # ── SMS ──────────────────────────────
    SMS_API_KEY: str = "placeholder"
    SMS_SENDER_ID: str = "TNZLKT"

    # ── Email ────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "placeholder"
    SMTP_PASSWORD: str = "placeholder"
    EMAIL_FROM: str = "noreply@tanzeelkart.com"

    # ── YouTube ──────────────────────────
    YOUTUBE_API_KEY: str = "placeholder"

    # ── RabbitMQ ─────────────────────────
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"

    # ── Delivery Settings ─────────────────
    MAX_DELIVERY_RADIUS_KM: float = 2.0
    MIN_ORDER_FOR_INSTANT_CHARGE: float = 50.0
    DELIVERY_CHARGE_DISCOUNT_500: float = 10.0
    DELIVERY_CHARGE_DISCOUNT_1000: float = 15.0
    DELIVERY_CHARGE_DISCOUNT_2000: float = 20.0

    # ── Location Defaults ─────────────────
    DEFAULT_BLOCK: str = "Reoti"
    DEFAULT_DISTRICT: str = "Ballia"
    DEFAULT_STATE: str = "Uttar Pradesh"
    DEFAULT_LAT: float = 26.0500
    DEFAULT_LON: float = 84.1800

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",
    }
