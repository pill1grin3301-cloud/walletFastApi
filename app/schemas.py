from click import File
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Mapped


class OperationRequest(BaseModel):
    wallet_name: str = Field(max_length=127)
    amount: float
    description: str | None = Field(None, max_length=255)

    @field_validator('amount')
    def amount_must_be_positive(cls, v: float) -> float:
        # Проверяем что значение больше нуля
        if v <= 0:
            raise ValueError('Amount must be positive')
        # Возвращаем значение если все ок
        return v
    
    @field_validator('wallet_name')
    def wallet_mame_not_empty(cls, v:str) -> str:
        # Убираем пробелы по краям
        v = v.strip()
        if not v:
            raise ValueError('Wallet_name cannot be empty')

        return v
    

class WalletUpdate(BaseModel):
    new_name: str = Field(max_length=127)

    @field_validator('new_name')
    def mame_not_empty(cls, v:str) -> str:
        # Убираем пробелы по краям
        v = v.strip()
        if not v:
            raise ValueError('Name cannot be empty')

        return v


class CreateWalletRequest(BaseModel):
    name: str = Field(max_length=127)
    initial_balance: float = 0

    @field_validator('name')
    def mame_not_empty(cls, v:str) -> str:
        # Убираем пробелы по краям
        v = v.strip()
        if not v:
            raise ValueError('Name cannot be empty')

        return v
    
    @field_validator('initial_balance')
    def balance_not_negative(cls, v: float) -> float:
        # Проверяем что значение больше нуля
        if v < 0:
            raise ValueError('Balance cannot be negative')
        # Возвращаем значение если все ок
        return v
    
    
class UserCreate(BaseModel):
    username: str = Field(max_length=42)
    password: str = Field(min_length=3)

class UserResponse(BaseModel):
    id: int
    username: str = Field(max_length=42)
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"