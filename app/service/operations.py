from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repository.wallets import WalletsRepository
from app.schemas import OperationRequest


class OperationService:
    def __init__(self, db: Session) -> None:
          self.db = db
          self.wallets_repository = WalletsRepository(db=db)


    def add_income(self, operation: OperationRequest) -> dict:
        # Проверяем существует ли такой кошелек
        if not self.wallets_repository.is_wallet_exist(operation.wallet_name):
                raise HTTPException(
                status_code=404,
                detail= f'Wallet {operation.wallet_name} not found'
                )
        
        # Добавляем доход к балансу кошелька
        wallet = self.wallets_repository.add_income(wallet_name=operation.wallet_name, amount=operation.amount)
        self.db.commit()
        # Выводим информацию об операции
        return {
            'message': f'Income added',
            'wallet': operation.wallet_name,
            'amount': operation.amount,
            'description': operation.description,
            "new_balance": wallet.balance
        }


    def add_expense(self, operation: OperationRequest) -> dict:
        # Проверяем существует ли такой кошелек
        if not self.wallets_repository.is_wallet_exist(operation.wallet_name):
            raise HTTPException(
            status_code=404,
            detail= f'Wallet {operation.wallet_name} not found'
            )
        
        # Проверяем достаточно ли средств
        wallet = self.wallets_repository.get_wallet_by_name(operation.wallet_name)
        if wallet.balance < operation.amount:
            # если денег недостаточно поднимаем ошибку 400
            raise HTTPException(
                status_code=400,
                detail=f'Insufficient funds. Available: {wallet.balance}'
            )
        
        # Вычитаем расход из баланса кошелька
        wallet = self.wallets_repository.add_expense(wallet_name=operation.wallet_name, amount=operation.amount)
        self.db.commit()

        # Возвращаем информацию
        return {
            'message': f'Expense added',
            'wallet': operation.wallet_name,
            'amount': operation.amount,
            'description': operation.description,
            "new_balance": wallet.balance
        }