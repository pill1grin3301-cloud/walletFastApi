
from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class WalletORM(Base):
    __tablename__ = 'wallets'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    balance: Mapped[Decimal]