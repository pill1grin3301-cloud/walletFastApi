from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import WalletORM

# class WalletsRepository:
#     def __init__(self, db: Session):
#         self.db = db
        

def is_wallet_exist(wallet_name: str, db: Session) -> bool:
    return db.query(WalletORM).filter(WalletORM.name == wallet_name).first() is not None


def add_income(wallet_name: str, amount: float, db: Session) -> WalletORM:
    wallet = db.query(WalletORM).filter(WalletORM.name == wallet_name).first()
    wallet.balance += amount
    db.commit()
    return wallet


def get_wallet_by_name(wallet_name: str, db: Session) -> WalletORM:
    wallet = db.query(WalletORM).filter(WalletORM.name == wallet_name).first()
    return wallet


def add_expense(wallet_name: str, amount: float, db: Session) -> WalletORM:
    wallet = db.query(WalletORM).filter(WalletORM.name == wallet_name).first()
    wallet.balance -= amount
    db.commit()
    return wallet


def get_all_wallets(db: Session) -> list[WalletORM]:
    return db.query(WalletORM).all()


def create(wallet_name: str, amount: float, db: Session) -> WalletORM:
    new_wallet = WalletORM(name=wallet_name, balance=amount)
    db.add(new_wallet)
    db.commit()
    db.refresh()
    return new_wallet

def delete(wallet_id: int, db: Session) -> None:
    del_wallet = db.query(WalletORM).filter(WalletORM.id == wallet_id).first()
    if not del_wallet:  
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet with id {wallet_id} not found"
        )
    db.delete(del_wallet)
    db.commit()
    