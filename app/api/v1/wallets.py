from fastapi import APIRouter

from app.schemas import CreateWalletRequest
from app.service import wallets as wallets_service

router = APIRouter(prefix='/api/v1', tags=['wallet'])


@router.get('/balance')
def get_balance(wallet_name: str | None = None):
    return wallets_service.get_wallet(wallet_name=wallet_name)

@router.post('/wallets')
def create_wallet(wallet: CreateWalletRequest):
    return wallets_service.create_wallet(wallet=wallet)

@router.delete('/{wallet_id}')
def delete_wallet(wallet_id: int):
    return wallets_service.delete_wallet(wallet_id=wallet_id)

