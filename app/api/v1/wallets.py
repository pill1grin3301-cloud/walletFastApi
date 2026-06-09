from fastapi import APIRouter, Depends, status

from app.api.v1.dependencies import get_current_user, get_wallet_service
from app.schemas import CreateWalletRequest, WalletUpdate
from app.service.wallets import WalletsService

router = APIRouter(prefix='/api/v1', tags=['wallet'])


@router.get('/balance')
def get_balance(wallets_service: WalletsService = Depends(get_wallet_service), current_user = Depends(get_current_user), wallet_name: str | None = None):
    return wallets_service.get_wallet(wallet_name=wallet_name, current_user=current_user)

@router.get('')
def get_all_wallets(wallets_service: WalletsService = Depends(get_wallet_service), current_user = Depends(get_current_user)):
    return wallets_service.get_all_wallets(current_user=current_user)

@router.patch('/{wallet_name}')
def rename_wallet(wallet_name: str, wallet_update: WalletUpdate, wallets_service: WalletsService = Depends(get_wallet_service), current_user = Depends(get_current_user)):
    result = wallets_service.rename_wallet(name=wallet_name, wallet_update=wallet_update, current_user=current_user)
    return result

@router.post('/wallets', status_code=status.HTTP_201_CREATED)
def create_wallet(wallet_data: CreateWalletRequest, wallets_service: WalletsService = Depends(get_wallet_service), current_user = Depends(get_current_user)):
    return wallets_service.create_wallet(wallet=wallet_data, current_user=current_user)

@router.delete('/{wallet_name}')
def delete_wallet(wallet_name: str, wallets_service: WalletsService = Depends(get_wallet_service), current_user = Depends(get_current_user)):
    return wallets_service.delete_wallet(wallet_name=wallet_name, current_user=current_user)

