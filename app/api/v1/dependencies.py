from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.service.operations import OperationService
from app.service.wallets import WalletsService


def get_wallet_service(db: Session = Depends(get_db)):
    return WalletsService(db)

def get_operation_service(db: Session = Depends(get_db)):
    return OperationService(db)