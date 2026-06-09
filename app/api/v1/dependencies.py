from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database import get_db
from app.models import UserORM
from app.service.auth import AuthService
from app.service.operations import OperationService
from app.service.wallets import WalletsService




security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserORM:
    auth_service = AuthService(db)
    return auth_service.get_current_user(credentials.credentials)

def get_auth_service(db: Session = Depends(get_db)):
    return AuthService(db)

def get_wallet_service(db: Session = Depends(get_db)):
    return WalletsService(db)

def get_operation_service(db: Session = Depends(get_db)):
    return OperationService(db)