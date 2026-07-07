from decimal import Decimal

from sqlalchemy.orm import Session, joinedload

from app.models import OperationORM, OperationType


class OperationsRepository():
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        user_id: str,
        wallet_id: str,
        type: OperationType,
        amount: float | Decimal,
        balance_after: Decimal,
        description: str | None = None,
    ) -> OperationORM:
        operation = OperationORM(
            user_id=user_id,
            wallet_id=wallet_id,
            type=type,
            amount=Decimal(amount),
            description=description,
            balance_after=balance_after,
        )
        self.db.add(operation)
        return operation

    def list_for_user(
        self,
        user_id: str,
        *,
        wallet_id: str | None = None,
        operation_type: OperationType | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[OperationORM], int]:
        query = (
            self.db.query(OperationORM)
            .options(joinedload(OperationORM.wallet))
            .filter(OperationORM.user_id == user_id)
        )
        if wallet_id is not None:
            query = query.filter(OperationORM.wallet_id == wallet_id)
        if operation_type is not None:
            query = query.filter(OperationORM.type == operation_type)

        total = query.count()
        items = (
            query.order_by(OperationORM.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total