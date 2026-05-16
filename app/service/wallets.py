
from fastapi import HTTPException

from app.repository import wallets as wallets_repository
from app.schemas import CreateWalletRequest


def get_wallet(wallet_name: str | None = None):
    # Если имя кошелька не указано - возвращаем общий баланс
    if wallet_name == None:
        wallets = wallets_repository.get_all_wallets()
        return {'total_balance': sum([w.balance for w in wallets])}
    
    # Проверяем существует ли запрашиваемый кошелек
    if not wallets_repository.is_wallet_exist(wallet_name=wallet_name):
        raise HTTPException(
            status_code=404,
            detail= f'Wallet {wallet_name} not found'
        )
    
    # Возвращаем баланс конкретного кошелька
    wallet = wallets_repository.get_wallet_by_name(wallet_name=wallet_name)
    return {"wallet:": wallet.name, 'balance:': wallet.balance}


def create_wallet(wallet: CreateWalletRequest):
    # Если кошелек существует, нам нужна ошибка
    if wallets_repository.is_wallet_exist(wallet_name=wallet.name):
        raise HTTPException(
            status_code=400,
            detail=f'Wallet {wallet.name} already exists'
        )
    # Если не существует создаем 
    wallet = wallets_repository.create(wallet_name=wallet.name, amount=wallet.inital_balance)

    # Возвращаем информацию об операции
    return {
        "message:": f"Wallet {wallet.name} created",
        "wallet:": wallet.name,
        "balance:": wallet.balance
    }

def delete_wallet(wallet_id: int) -> str:
    wallets_repository.delete(wallet_id=wallet_id)
    return "Wallet deleted successfuly"