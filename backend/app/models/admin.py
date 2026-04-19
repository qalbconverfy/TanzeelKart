from sqlalchemy import (
    Column, String, Boolean,
    DateTime, JSON, ForeignKey,
    Integer,
)
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class Admin(BaseModel):
    __tablename__ = "admins"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    username = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )
    hashed_password = Column(
        String(255), nullable=False
    )

    # Biometric
    biometric_enabled = Column(
        Boolean, default=False
    )
    biometric_key = Column(
        String(500), nullable=True
    )

    # Permissions
    is_super_admin = Column(Boolean, default=False)
    permissions = Column(JSON, nullable=True)

    # Security
    last_login = Column(
        DateTime(timezone=True), nullable=True
    )
    failed_attempts = Column(Integer, default=0)
    is_locked = Column(Boolean, default=False)
    added_by = Column(
        UUID(as_uuid=True), nullable=True
    )
