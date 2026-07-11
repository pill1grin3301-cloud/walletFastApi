from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class OperationRequest(BaseModel):
    wallet_name: str = Field(max_length=127)
    amount: float
    description: str | None = Field(None, max_length=255)

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v

    @field_validator("wallet_name")
    @classmethod
    def wallet_name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Wallet_name cannot be empty")
        return v


class OperationResponse(BaseModel):
    id: str
    type: Literal["income", "expense"]
    amount: float
    description: str | None
    wallet_name: str
    balance_after: float
    created_at: datetime

    model_config = {"from_attributes": True}


class OperationListResponse(BaseModel):
    items: list[OperationResponse]
    total: int
    limit: int
    offset: int


class WalletUpdate(BaseModel):
    new_name: str = Field(max_length=127)

    @field_validator("new_name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        return v


class CreateWalletRequest(BaseModel):
    name: str = Field(max_length=127)
    initial_balance: float = 0

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        return v

    @field_validator("initial_balance")
    @classmethod
    def balance_not_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Balance cannot be negative")
        return v


class UserCreateAndLogin(BaseModel):
    username: str = Field(max_length=42)
    password: str = Field(min_length=3)


class UserResponse(BaseModel):
    id: str
    username: str = Field(max_length=42)
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
