from pydantic import BaseModel, Field, field_validator
from decimal import Decimal

class OperationRequest(BaseModel):
    wallet_name: str = Field(max_length=127)
    amount: Decimal
    description: str | None = Field(None, max_length=255)

    @field_validator('amount')
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        # Проверяем что значение больше нуля
        if v <= 0:
            raise ValueError('Amount must be positive')
        # Возвращаем значение если все ок
        return v
    
    @field_validator('wallet_name')
    def wallet_name_not_empty(cls, v:str) -> str:
        # Убираем пробелы по краям
        v = v.strip()
        if not v:
            raise ValueError('Wallet_name cannot be empty')

        return v
    

class WalletUpdate(BaseModel):
    new_name: str = Field(max_length=127)

    @field_validator('new_name')
    def name_not_empty(cls, v:str) -> str:
        # Убираем пробелы по краям
        v = v.strip()
        if not v:
            raise ValueError('Name cannot be empty')

        return v


class CreateWalletRequest(BaseModel):
    name: str = Field(max_length=127)
    initial_balance: Decimal = 0

    @field_validator('name')
    def name_not_empty(cls, v:str) -> str:
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