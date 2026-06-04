
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from app.database import Base


class WalletORM(Base):
    __tablename__ = 'wallets'
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str]
    balance: Mapped[Decimal]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["UserORM"] = relationship(back_populates="wallets")


class UserORM(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    wallets: Mapped[list["WalletORM"]] = relationship(
        "WalletORM",                # какая модель с другой стороны
        back_populates="user",      # имя поля в WalletORM
        cascade="all, delete-orphan" # при удалении пользователя удалить и кошельки
    )
    
