from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import WalletORM
from app.schemas import WalletUpdate

class WalletsRepository:
    def __init__(self, db: Session):
        self.db = db
        
    # Проверка существования кошелька
    def is_wallet_exist(self, wallet_name: str) -> bool:
        return self.db.query(WalletORM).filter(WalletORM.name == wallet_name).first() is not None

    # Функия добавления дохода к балансу
    def add_income(self, wallet_name: str, amount: float) -> WalletORM:
        wallet = self.db.query(WalletORM).filter(WalletORM.name == wallet_name).first()
        wallet.balance += Decimal(amount)
        return wallet

    # Найти кошелек по имени
    def get_wallet_by_name(self, wallet_name: str) -> WalletORM:
        wallet = self.db.query(WalletORM).filter(WalletORM.name == wallet_name).first()
        return wallet
    
    # Функция добавления трат
    def add_expense(self, wallet_name: str, amount: float) -> WalletORM:
        wallet = self.db.query(WalletORM).filter(WalletORM.name == wallet_name).first()
        wallet.balance -= Decimal(amount)
        return wallet

    # Возвращате список всех кошельков
    def get_all(self) -> list[WalletORM]:
        return self.db.query(WalletORM).all()


    def create(self, wallet_name: str, amount: float) -> WalletORM:
        new_wallet = WalletORM(name=wallet_name, balance=amount)
        return new_wallet
    
    def update_wallet(self, wallet_name: str, wallet_update: WalletUpdate) -> WalletORM:
        wallet = self.db.query(WalletORM).filter(WalletORM.name == wallet_name).first()
        wallet.name = wallet_update.new_name
        return wallet

    def delete(self, wallet_name: str) -> None:
        del_wallet = self.db.query(WalletORM).filter(WalletORM.name == wallet_name).first()
        if not del_wallet:  
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wallet {wallet_name} not found"
            )
        self.db.delete(del_wallet)
    