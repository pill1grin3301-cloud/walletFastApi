from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import WalletORM
from app.schemas import WalletUpdate


class WalletsRepository:
    def __init__(self, db: Session):
        self.db = db

    # Проверка существования кошелька по имени и user_id
    def is_wallet_exist(self, wallet_name: str, user_id: str) -> bool:
        return self.db.query(WalletORM).filter(
            WalletORM.name == wallet_name,
            WalletORM.user_id == user_id
        ).first() is not None

    # Добавление дохода к балансу
    def add_income(self, wallet_name: str, amount: float, user_id: str) -> WalletORM:
        wallet = self.db.query(WalletORM).filter(
            WalletORM.name == wallet_name,
            WalletORM.user_id == user_id
        ).first()
        if not wallet:
            raise HTTPException(404, f"Wallet {wallet_name} not found")
        wallet.balance += Decimal(amount)
        return wallet

    # Найти кошелек по имени и user_id
    def get_wallet_by_name(self, wallet_name: str, user_id: str) -> WalletORM | None:
        return self.db.query(WalletORM).filter(
            WalletORM.name == wallet_name,
            WalletORM.user_id == user_id
        ).first()
    
    # 

    # Добавление расхода
    def add_expense(self, wallet_name: str, amount: float, user_id: str) -> WalletORM:
        wallet = self.db.query(WalletORM).filter(
            WalletORM.name == wallet_name,
            WalletORM.user_id == user_id
        ).first()
        if not wallet:
            raise HTTPException(404, f"Wallet {wallet_name} not found")
        wallet.balance -= Decimal(amount)
        return wallet

    # Получить все кошельки пользователя
    def get_all_by_user(self, user_id: str) -> list[WalletORM]:
        return self.db.query(WalletORM).filter(WalletORM.user_id == user_id).all()
    


    # Создать кошелёк (user_id теперь обязателен)
    def create(self, wallet_name: str, amount: float, user_id: str) -> WalletORM:
        new_wallet = WalletORM(name=wallet_name, balance=Decimal(amount), user_id=user_id)
        return new_wallet

    # Обновить имя кошелька
    def update_wallet(self, wallet_name: str, wallet_update: WalletUpdate, user_id: str) -> WalletORM:
        wallet = self.db.query(WalletORM).filter(
            WalletORM.name == wallet_name,
            WalletORM.user_id == user_id
        ).first()
        if not wallet:
            raise HTTPException(404, f"Wallet {wallet_name} not found")
        wallet.name = wallet_update.new_name
        return wallet

    # Удалить кошелёк
    def delete(self, wallet_name: str, user_id: str) -> None:
        del_wallet = self.db.query(WalletORM).filter(
            WalletORM.name == wallet_name,
            WalletORM.user_id == user_id
        ).first()
        if not del_wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wallet {wallet_name} not found"
            )
        self.db.delete(del_wallet)