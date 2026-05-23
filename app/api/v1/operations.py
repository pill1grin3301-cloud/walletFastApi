from fastapi import APIRouter, Depends
from api.v1.dependencies import get_operation_service
from schemas import OperationRequest
from service.operations import OperationService

router = APIRouter(prefix='/api/v1/operations', tags=['operations'])

@router.post('/income')
def add_income(operation: OperationRequest, operation_service: OperationService = Depends(get_operation_service)) -> dict:
    return operation_service.add_income(operation=operation)
    

@router.post('/expense')
def add_expense(operation: OperationRequest, operation_service: OperationService = Depends(get_operation_service)) -> dict:
    return operation_service.add_expense(operation=operation)