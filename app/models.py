import enum
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import sqlalchemy
from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WalletORM(Base):
    __tablename__ = "wallets"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_wallet_user_name"),)

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str]
    balance: Mapped[Decimal]
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    user: Mapped["UserORM"] = relationship(back_populates="wallets")
    operations: Mapped[list["OperationORM"]] = relationship(
        back_populates="wallet",
        cascade="all, delete-orphan",
    )


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    wallets: Mapped[list["WalletORM"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    operations: Mapped[list["OperationORM"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class OperationType(enum.StrEnum):
    income = "income"
    expense = "expense"


class OperationORM(Base):
    __tablename__ = "operations"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    wallet_id: Mapped[str] = mapped_column(ForeignKey("wallets.id", ondelete="CASCADE"))
    type: Mapped[OperationType] = mapped_column(
        sqlalchemy.Enum(OperationType, name="operation_type"),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    balance_after: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    user: Mapped["UserORM"] = relationship(back_populates="operations")
    wallet: Mapped["WalletORM"] = relationship(back_populates="operations")
