
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class WalletORM(Base):
    __tablename__ = 'wallets'
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str]
    balance: Mapped[Decimal]