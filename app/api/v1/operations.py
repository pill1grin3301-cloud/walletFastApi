from fastapi import APIRouter, Depends, Query

from app.api.v1.dependencies import get_current_user, get_operation_service
from app.models import OperationType
from app.schemas import OperationListResponse, OperationRequest, OperationResponse
from app.service.operations import OperationService

router = APIRouter(prefix='/api/v1/operations', tags=['operations'])


@router.get('', response_model=OperationListResponse)
def list_operations(
    wallet_name: str | None = None,
    operation_type: OperationType | None = Query(None, alias='type'),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user=Depends(get_current_user),
    operation_service: OperationService = Depends(get_operation_service),
) -> OperationListResponse:
    return operation_service.get_history(
        current_user,
        wallet_name=wallet_name,
        operation_type=operation_type,
        limit=limit,
        offset=offset,
    )


@router.post('/income', response_model=OperationResponse)
def add_income(
    operation: OperationRequest,
    current_user=Depends(get_current_user),
    operation_service: OperationService = Depends(get_operation_service),
) -> dict:
    return operation_service.add_income(operation=operation, current_user=current_user)


@router.post('/expense', response_model=OperationResponse)
def add_expense(
    operation: OperationRequest,
    current_user=Depends(get_current_user),
    operation_service: OperationService = Depends(get_operation_service),
) -> dict:
    return operation_service.add_expense(operation=operation, current_user=current_user)
