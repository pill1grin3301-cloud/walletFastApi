from fastapi import HTTPException, status
from sqlalchemy.orm import Session


from app.models import WalletORM
from app.repository.wallets import WalletsRepository
from app.schemas import CreateWalletRequest, WalletUpdate

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
            wallets = self.wallets_repository.get_all()
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
    

    def rename_wallet(self, name: str, wallet_update: WalletUpdate) -> WalletORM:
        if not self.wallets_repository.is_wallet_exist(name):
            raise HTTPException(
                status_code=404, # Not exist this wallet
                detail= f'Wallet {name} not found'
            )
        
        if name == wallet_update.new_name:
            raise HTTPException(
                status_code=409,
                detail= f"This Wallet already names {name}, please enter a new name"
            )
        
        if self.wallets_repository.is_wallet_exist(wallet_update.new_name):
            raise HTTPException(
                status_code=409,  # Conflict
                detail=f"Wallet with name '{wallet_update.new_name}' already exists"
            )
        

        wallet = self.wallets_repository.update_wallet(wallet_name=name, wallet_update=wallet_update)
        self.db.commit()    
        self.db.refresh(wallet)
        return wallet
    

    def create_wallet(self, wallet: CreateWalletRequest):
        # Если кошелек существует, нам нужна ошибка
        if self.wallets_repository.is_wallet_exist(wallet_name=wallet.name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'Wallet {wallet.name} already exists'
            )
        # Если не существует создаем 
        wallet = self.wallets_repository.create(wallet_name=wallet.name, amount=wallet.initial_balance)
        self.db.add(wallet)
        self.db.commit()
        self.db.refresh(wallet)
        # Возвращаем информацию об операции
        return {
            "message": f"Wallet {wallet.name} created",
            "wallet": wallet.name,
            "balance": wallet.balance
        }
    

    def delete_wallet(self, wallet_name: str):
        self.wallets_repository.delete(wallet_name=wallet_name)
        self.db.commit()
        return f"Wallet {wallet_name} deleted successfuly"