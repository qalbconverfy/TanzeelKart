from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "TanzeelKart"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str
    ALLOWED_HOSTS: List[str] = ["*"]
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str
    SYNC_DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # InfluxDB
    INFLUXDB_URL: str
    INFLUXDB_TOKEN: str
    INFLUXDB_ORG: str
    INFLUXDB_BUCKET: str

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OTP
    OTP_EXPIRE_MINUTES: int = 10

    # SMS
    SMS_API_KEY: str
    SMS_SENDER_ID: str = "TNZLKT"

    # Email
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str

    # YouTube
    YOUTUBE_API_KEY: str

    # RabbitMQ
    RABBITMQ_URL: str

    # Delivery Settings
    MAX_DELIVERY_RADIUS_KM: float = 2.0
    MIN_ORDER_FOR_DELIVERY_CHARGE: float = 50.0
    DELIVERY_CHARGE_DISCOUNT_THRESHOLD: float = 500.0

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()