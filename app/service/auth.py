from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import UserORM
from app.schemas import UserCreateAndLogin
from app.service.telegram_notify import notify_del_user, notify_new_user

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    def register(self, data: UserCreateAndLogin) -> UserORM:
        existing = self.db.query(UserORM).filter(UserORM.username == data.username).first()
        if existing:
            raise HTTPException(status_code=409, detail="Username already taken")

        user = UserORM(
            username=data.username,
            hashed_password=self.hash_password(data.password),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        notify_new_user(user.username)
        return user

    def login(self, data: UserCreateAndLogin) -> str:
        user = self.db.query(UserORM).filter(UserORM.username == data.username).first()
        if not user or not self.verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = jwt.encode(
            {"sub": str(user.id), "exp": datetime.now(timezone.utc) + timedelta(hours=24)},
            SECRET_KEY,
            algorithm=ALGORITHM,
        )
        return token

    def get_current_user(self, token: str) -> UserORM:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
        except Exception as e:
            print(f"Error: {e}")
            raise HTTPException(status_code=401, detail="Invalid token") from e

        user = self.db.query(UserORM).filter(UserORM.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user

    def delete_user(self, user_id: str) -> None:
        user = self.db.query(UserORM).filter(UserORM.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        name = user.username
        self.db.delete(user)
        self.db.commit()
        notify_del_user(username=name)
