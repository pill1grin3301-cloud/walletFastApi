from fastapi import HTTPException
from sqlalchemy.orm import Session


from app.models import WalletORM
from app.repository.wallets import WalletsRepository
from app.schemas import CreateWalletRequest

class WalletsService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.wallets_repository = WalletsRepository(db)


    def get_all_wallets(self) -> list[WalletORM]:
        walllets_orm =  self.wallets_repository.get_all()
        return walllets_orm

    def get_wallet(self, wallet_name: str | None = None):
        # Если имя кошелька не указано - возвращаем общий баланс
        if wallet_name == None:
            wallets = self.wallets_repository.get_all_wallets()
            return {'total_balance': sum([w.balance for w in wallets])}
        
        # Проверяем существует ли запрашиваемый кошелек
        if not self.wallets_repository.is_wallet_exist(wallet_name=wallet_name):
            raise HTTPException(
                status_code=404,
                detail= f'Wallet {wallet_name} not found'
            )
        
        # Возвращаем баланс конкретного кошелька
        wallet = self.wallets_repository.get_wallet_by_name(wallet_name=wallet_name)
        return {"wallet:": wallet.name, 'balance:': wallet.balance}


    def create_wallet(self, wallet: CreateWalletRequest):
        # Если кошелек существует, нам нужна ошибка
        if self.wallets_repository.is_wallet_exist(wallet_name=wallet.name):
            raise HTTPException(
                status_code=400,
                detail=f'Wallet {wallet.name} already exists'
            )
        # Если не существует создаем 
        wallet = self.wallets_repository.create(wallet_name=wallet.name, amount=wallet.initial_balance)

        # Возвращаем информацию об операции
        return {
            "message:": f"Wallet {wallet.name} created",
            "wallet:": wallet.name,
            "balance:": wallet.balance
        }

    def delete_wallet(self, wallet_name: str) -> str:
        self.wallets_repository.delete(wallet_name=wallet_name)
        return f"Wallet {wallet_name} deleted successfuly"