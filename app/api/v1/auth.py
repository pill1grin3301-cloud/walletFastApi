from fastapi import APIRouter, Depends, status

from app.api.v1.dependencies import get_auth_service, get_current_user
from app.models import UserORM
from app.schemas import Token, UserCreateAndLogin

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=Token)
def register(data: UserCreateAndLogin, auth = Depends(get_auth_service)):
    user = auth.register(data)
    token = auth.login(data)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(data: UserCreateAndLogin, auth = Depends(get_auth_service)):
    token = auth.login(data)
    return {"access_token": token, "token_type": "bearer"}

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete(current_user: UserORM = Depends(get_current_user), auth = Depends(get_auth_service)):
    auth.delete_user(current_user.id)

