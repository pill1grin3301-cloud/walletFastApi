from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import WalletORM

class WalletsRepository:
    def __init__(self, db: Session):
        self.db = db
        

    def is_wallet_exist(self, wallet_name: str) -> bool:
        return self.db.query(WalletORM).filter(WalletORM.name == wallet_name).first() is not None


    def add_income(self, wallet_name: str, amount: float) -> WalletORM:
        wallet = self.db.query(WalletORM).filter(WalletORM.name == wallet_name).first()
        wallet.balance += amount
        self.db.commit()
        return wallet


    def get_wallet_by_name(self, wallet_name: str) -> WalletORM:
        wallet = self.db.query(WalletORM).filter(WalletORM.name == wallet_name).first()
        return wallet


    def add_expense(self, wallet_name: str, amount: float) -> WalletORM:
        wallet = self.db.query(WalletORM).filter(WalletORM.name == wallet_name).first()
        wallet.balance -= amount
        self.db.commit()
        return wallet


    def get_all_wallets(self) -> list[WalletORM]:
        return self.db.query(WalletORM).all()


    def create(self, wallet_name: str, amount: float) -> WalletORM:
        new_wallet = WalletORM(name=wallet_name, balance=amount)
        self.db.add(new_wallet)
        self.db.commit()
        self.db.refresh(new_wallet)
        return new_wallet

    def delete(self, wallet_id: int) -> None:
        del_wallet = self.db.query(WalletORM).filter(WalletORM.id == wallet_id).first()
        if not del_wallet:  
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wallet with id {wallet_id} not found"
            )
        self.db.delete(del_wallet)
        self.db.commit()
    