from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import OperationORM, OperationType, UserORM
from app.repository.operations import OperationsRepository
from app.repository.wallets import WalletsRepository
from app.schemas import OperationListResponse, OperationRequest, OperationResponse
from app.service.telegram_notify import notify_new_expense, notify_new_income


class OperationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.wallets_repository = WalletsRepository(db)
        self.operations_repository = OperationsRepository(db)

    @staticmethod
    def _to_response(operation: OperationORM) -> OperationResponse:
        return OperationResponse(
            id=operation.id,
            type=operation.type.value,
            amount=float(operation.amount),
            description=operation.description,
            wallet_name=operation.wallet.name,
            balance_after=float(operation.balance_after),
            created_at=operation.created_at,
        )

    def get_history(
        self,
        current_user: UserORM,
        *,
        wallet_name: str | None = None,
        operation_type: OperationType | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> OperationListResponse:
        limit = min(max(limit, 1), 100)
        offset = max(offset, 0)

        wallet_id = None
        if wallet_name is not None:
            wallet = self.wallets_repository.get_wallet_by_name(wallet_name, current_user.id)
            if wallet is None:
                raise HTTPException(status_code=404, detail=f"Wallet {wallet_name} not found")
            wallet_id = wallet.id

        operations, total = self.operations_repository.list_for_user(
            current_user.id,
            wallet_id=wallet_id,
            operation_type=operation_type,
            limit=limit,
            offset=offset,
        )
        return OperationListResponse(
            items=[self._to_response(op) for op in operations],
            total=total,
            limit=limit,
            offset=offset,
        )

    def add_income(self, operation: OperationRequest, current_user: UserORM) -> OperationResponse:
        if not self.wallets_repository.is_wallet_exist(operation.wallet_name, current_user.id):
            raise HTTPException(status_code=404, detail=f"Wallet {operation.wallet_name} not found")

        wallet = self.wallets_repository.add_income(
            operation.wallet_name,
            operation.amount,
            current_user.id,
        )
        new_operation = self.operations_repository.create(
            user_id=current_user.id,
            wallet_id=wallet.id,
            type=OperationType.income,
            amount=operation.amount,
            balance_after=wallet.balance,
            description=operation.description,
        )
        self.db.commit()
        self.db.refresh(new_operation)
        notify_new_income(
            username=current_user.username,
            wallet_name=operation.wallet_name,
            amount=operation.amount,
        )
        return self._to_response(new_operation)

    def add_expense(self, operation: OperationRequest, current_user: UserORM) -> OperationResponse:
        if not self.wallets_repository.is_wallet_exist(operation.wallet_name, current_user.id):
            raise HTTPException(status_code=404, detail=f"Wallet {operation.wallet_name} not found")

        wallet = self.wallets_repository.get_wallet_by_name(operation.wallet_name, current_user.id)
        if wallet.balance < operation.amount:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient funds. Available: {wallet.balance}",
            )

        wallet = self.wallets_repository.add_expense(
            operation.wallet_name,
            operation.amount,
            current_user.id,
        )
        new_operation = self.operations_repository.create(
            user_id=current_user.id,
            wallet_id=wallet.id,
            type=OperationType.expense,
            amount=operation.amount,
            balance_after=wallet.balance,
            description=operation.description,
        )
        self.db.commit()
        self.db.refresh(new_operation)
        notify_new_expense(
            username=current_user.username,
            wallet_name=operation.wallet_name,
            amount=operation.amount,
        )
        return self._to_response(new_operation)
