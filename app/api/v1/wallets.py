from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_wallet_service
from app.models import WalletORM
from app.schemas import CreateWalletRequest
from app.service.wallets import WalletsService

router = APIRouter(prefix='/api/v1', tags=['wallet'])


@router.get('/balance')
def get_balance(wallets_service: WalletsService = Depends(get_wallet_service), wallet_name: str | None = None):
    return wallets_service.get_wallet(wallet_name=wallet_name)

@router.get('')
def get_all_wallets(wallets_service: WalletsService = Depends(get_wallet_service)):
    return wallets_service.get_all_wallets()    

@router.post('/wallets')
def create_wallet(wallet_data: CreateWalletRequest, wallets_service: WalletsService = Depends(get_wallet_service)):
    return wallets_service.create_wallet(wallet=wallet_data)

@router.delete('/{wallet_name}')
def delete_wallet(wallet_name: str, wallets_service: WalletsService = Depends(get_wallet_service)):
    return wallets_service.delete_wallet(wallet_name=wallet_name)

