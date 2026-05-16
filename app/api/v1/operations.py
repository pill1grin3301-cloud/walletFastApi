from fastapi import APIRouter
from app.service import operations as operations_service
from app.schemas import OperationRequest

router = APIRouter(prefix='/api/v1/operations', tags=['operations'])

@router.post('/income')
def add_income(operation: OperationRequest):
    return operations_service.add_income(operation=operation)
    

@router.post('/expense')
def add_expense(operation: OperationRequest):
    return operations_service.add_expense(operation=operation)