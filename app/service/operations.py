from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repository.wallets import WalletsRepository
from app.schemas import OperationRequest


class OperationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.wallets_repository = WalletsRepository(db=db)

    def add_income(self, operation: OperationRequest, current_user) -> dict:
        # Проверяем существует ли кошелек у пользователя
        if not self.wallets_repository.is_wallet_exist(operation.wallet_name, current_user.id):
            raise HTTPException(
                status_code=404,
                detail=f'Wallet {operation.wallet_name} not found'
            )

        # Добавляем доход к балансу кошелька
        wallet = self.wallets_repository.add_income(operation.wallet_name, operation.amount, current_user.id)
        self.db.commit()

        return {
            'message': 'Income added',
            'wallet': operation.wallet_name,
            'amount': operation.amount,
            'description': operation.description,
            "new_balance": wallet.balance
        }
    

    def add_expense(self, operation: OperationRequest, current_user) -> dict:
        # Проверяем существует ли кошелек у пользователя
        if not self.wallets_repository.is_wallet_exist(operation.wallet_name, current_user.id):
            raise HTTPException(
                status_code=404,
                detail=f'Wallet {operation.wallet_name} not found'
            )

        # Проверяем достаточно ли средств
        wallet = self.wallets_repository.get_wallet_by_name(operation.wallet_name, current_user.id)
        if wallet.balance < operation.amount:
            raise HTTPException(
                status_code=400,
                detail=f'Insufficient funds. Available: {wallet.balance}'
            )

        # Вычитаем расход из баланса кошелька
        wallet = self.wallets_repository.add_expense(operation.wallet_name, operation.amount, current_user.id)
        self.db.commit()

        return {
            'message': 'Expense added',
            'wallet': operation.wallet_name,
            'amount': operation.amount,
            'description': operation.description,
            "new_balance": wallet.balance
        }