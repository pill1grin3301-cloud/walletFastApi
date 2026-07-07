

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import OperationType, WalletORM
from app.repository.operations import OperationsRepository
from app.repository.wallets import WalletsRepository
from app.schemas import CreateWalletRequest, WalletUpdate
from app.service.telegram_notify import notify_del_wallet, notify_new_wallet


class WalletsService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.wallets_repository = WalletsRepository(db)
        self.operations_repository = OperationsRepository(db=db)

    def get_all_wallets(self, current_user) -> list[WalletORM]:
        wallets_orm = self.wallets_repository.get_all_by_user(current_user.id)
        return wallets_orm

    def get_wallet(self, wallet_name: str | None, current_user):
        # Если имя кошелька не указано - возвращаем общий баланс
        if wallet_name is None:
            wallets = self.wallets_repository.get_all_by_user(current_user.id)
            return {'total_balance': sum(w.balance for w in wallets)}
        
        # Проверяем существует ли запрашиваемый кошелек у пользователя
        if not self.wallets_repository.is_wallet_exist(wallet_name, current_user.id):
            raise HTTPException(
                status_code=404,
                detail=f'Wallet {wallet_name} not found'
            )
        
        # Возвращаем баланс конкретного кошелька
        wallet = self.wallets_repository.get_wallet_by_name(wallet_name, current_user.id)
        return {"wallet": wallet.name, "balance": wallet.balance}

    def rename_wallet(self, name: str, wallet_update: WalletUpdate, current_user) -> WalletORM:
        if not self.wallets_repository.is_wallet_exist(name, current_user.id):
            raise HTTPException(
                status_code=404,
                detail=f'Wallet {name} not found'
            )
        
        if name == wallet_update.new_name:
            raise HTTPException(
                status_code=409,
                detail=f"This wallet already named {name}, please enter a new name"
            )
        
        if self.wallets_repository.is_wallet_exist(wallet_update.new_name, current_user.id):
            raise HTTPException(
                status_code=409,
                detail=f"Wallet with name '{wallet_update.new_name}' already exists"
            )
        
        wallet = self.wallets_repository.update_wallet(name, wallet_update, current_user.id)
        self.db.commit()
        self.db.refresh(wallet)
        return wallet

    def create_wallet(self, wallet: CreateWalletRequest, current_user):
        # Если кошелек с таким именем уже существует у пользователя
        if self.wallets_repository.is_wallet_exist(wallet.name, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'Wallet {wallet.name} already exists'
            )
        
        # Создаём кошелёк с привязкой к пользователю
        new_wallet = self.wallets_repository.create(wallet.name, wallet.initial_balance, current_user.id)
        self.db.add(new_wallet)
        self.db.flush()  # id кошелька нужен до записи операции
        if wallet.initial_balance > 0:
            self.operations_repository.create(
                user_id=current_user.id,
                wallet_id=new_wallet.id,
                type=OperationType.income,
                amount=wallet.initial_balance,
                balance_after=new_wallet.balance,
                description="Initial Balance",
            )
        self.db.commit()
        self.db.refresh(new_wallet)
        notify_new_wallet(current_user.username, new_wallet.name)

        return {
            "message": f"Wallet {new_wallet.name} created",
            "wallet": new_wallet.name,
            "balance": new_wallet.balance
        }

    def delete_wallet(self, wallet_name: str, current_user):
        self.wallets_repository.delete(wallet_name, current_user.id)
        self.db.commit()
        notify_del_wallet(username=current_user.username, wallet_name=wallet_name)
        return f"Wallet {wallet_name} deleted successfully"