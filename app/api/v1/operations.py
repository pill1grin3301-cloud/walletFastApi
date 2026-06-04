from fastapi import APIRouter, Depends
from app.api.v1.dependencies import get_current_user, get_operation_service
from app.schemas import OperationRequest
from app.service.operations import OperationService

router = APIRouter(prefix='/api/v1/operations', tags=['operations'])

@router.post('/income')
def add_income(operation: OperationRequest, current_user = Depends(get_current_user), operation_service: OperationService = Depends(get_operation_service)) -> dict:
    return operation_service.add_income(operation=operation, current_user=current_user)
    

@router.post('/expense')
def add_expense(operation: OperationRequest, current_user = Depends(get_current_user), operation_service: OperationService = Depends(get_operation_service)) -> dict:
    return operation_service.add_expense(operation=operation, current_user=current_user)