from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone

from app.models import UserORM
from app.schemas import UserCreate
from app.core.config import settings
from app.service.telegram_notify import notify_new_user

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)
    
    def register(self, data: UserCreate) -> UserORM:
        # Проверка на существующего пользователя
        existing = self.db.query(UserORM).filter(UserORM.username == data.username).first()
        if existing:
            raise HTTPException(409, "Username already taken")
        
        user = UserORM(
            username=data.username,
            hashed_password=self.hash_password(data.password)
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        notify_new_user(user.username)
        return user
    
    def login(self, username: str, password: str) -> str:
        user = self.db.query(UserORM).filter(UserORM.username == username).first()
        if not user or not self.verify_password(password, user.hashed_password):
            raise HTTPException(401, "Invalid credentials")
        
        token = jwt.encode(
            {"sub": str(user.id), "exp": datetime.now(timezone.utc) + timedelta(hours=24)},
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        return token
    
    def get_current_user(self, token: str) -> UserORM:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
        except Exception as e:
            print(f'Error: {e}')
            raise HTTPException(401, "Invalid token")
        
        user = self.db.query(UserORM).filter(UserORM.id == user_id).first()
        if not user:
            raise HTTPException(401, "User not found")
        return user
    

    def delete_user(self, user_id: str):
        user = self.db.query(UserORM).filter(UserORM.id == user_id).first()
        if not user:
            raise HTTPException(404, "User not found")
        self.db.delete(user)
        self.db.commit()
        