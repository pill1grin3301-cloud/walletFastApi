from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import WalletORM
from app.schemas import WalletUpdate


class WalletsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def is_wallet_exist(self, wallet_name: str, user_id: str) -> bool:
        return (
            self.db.query(WalletORM)
            .filter(WalletORM.name == wallet_name, WalletORM.user_id == user_id)
            .first()
            is not None
        )

    def get_wallet_by_name(self, wallet_name: str, user_id: str) -> WalletORM | None:
        return (
            self.db.query(WalletORM)
            .filter(WalletORM.name == wallet_name, WalletORM.user_id == user_id)
            .first()
        )

    def get_all_by_user(self, user_id: str) -> list[WalletORM]:
        return self.db.query(WalletORM).filter(WalletORM.user_id == user_id).all()

    def create(self, wallet_name: str, amount: float, user_id: str) -> WalletORM:
        # ORM-объект; add/flush делает сервис
        return WalletORM(name=wallet_name, balance=Decimal(amount), user_id=user_id)

    def add_income(self, wallet_name: str, amount: float, user_id: str) -> WalletORM:
        wallet = self.get_wallet_by_name(wallet_name, user_id)
        if not wallet:
            raise HTTPException(status_code=404, detail=f"Wallet {wallet_name} not found")
        wallet.balance += Decimal(amount)
        return wallet

    def add_expense(self, wallet_name: str, amount: float, user_id: str) -> WalletORM:
        wallet = self.get_wallet_by_name(wallet_name, user_id)
        if not wallet:
            raise HTTPException(status_code=404, detail=f"Wallet {wallet_name} not found")
        wallet.balance -= Decimal(amount)
        return wallet

    def update_wallet(
        self,
        wallet_name: str,
        wallet_update: WalletUpdate,
        user_id: str,
    ) -> WalletORM:
        wallet = self.get_wallet_by_name(wallet_name, user_id)
        if not wallet:
            raise HTTPException(status_code=404, detail=f"Wallet {wallet_name} not found")
        wallet.name = wallet_update.new_name
        return wallet

    def delete(self, wallet_name: str, user_id: str) -> None:
        wallet = self.get_wallet_by_name(wallet_name, user_id)
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wallet {wallet_name} not found",
            )
        self.db.delete(wallet)
