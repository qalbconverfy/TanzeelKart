import enum
from sqlalchemy import (
    Column, Float, String,
    Enum, ForeignKey, Boolean,
    DateTime, Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel


class WalletType(str, enum.Enum):
    SHOP = "shop"
    PLATFORM = "platform"
    DELIVERY = "delivery"
    USER = "user"


class TransactionType(str, enum.Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    COMMISSION = "commission"
    WITHDRAWAL = "withdrawal"
    REFUND = "refund"


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class Wallet(BaseModel):
    __tablename__ = "wallets"

    # Owner
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    shop_id = Column(
        UUID(as_uuid=True),
        ForeignKey("shops.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    wallet_type = Column(
        Enum(WalletType),
        nullable=False,
    )

    # Balance
    balance = Column(Float, default=0.0)
    total_earned = Column(Float, default=0.0)
    total_withdrawn = Column(Float, default=0.0)
    pending_amount = Column(Float, default=0.0)

    # Status
    is_frozen = Column(Boolean, default=False)

    # Relationships
    user = relationship(
        "User", back_populates="wallet"
    )
    shop = relationship(
        "Shop", back_populates="wallet"
    )
    transactions = relationship(
        "WalletTransaction",
        back_populates="wallet",
    )


class WalletTransaction(BaseModel):
    __tablename__ = "wallet_transactions"

    wallet_id = Column(
        UUID(as_uuid=True),
        ForeignKey("wallets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="SET NULL"),
        nullable=True,
    )

    type = Column(
        Enum(TransactionType),
        nullable=False,
    )
    status = Column(
        Enum(TransactionStatus),
        default=TransactionStatus.SUCCESS,
    )

    amount = Column(Float, nullable=False)
    commission_amount = Column(
        Float, default=0.0
    )
    net_amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    reference_id = Column(
        String(100), nullable=True
    )

    # Relationships
    wallet = relationship(
        "Wallet",
        back_populates="transactions",
    )
