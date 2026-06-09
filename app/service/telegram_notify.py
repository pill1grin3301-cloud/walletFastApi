import httpx

from app.core.config import settings

_HTTP_TIMEOUT = httpx.Timeout(connect=10.0, read=15.0, write=10.0, pool=10.0)


def _send(text: str) -> None:
    if not settings.TELEGRAM_TOKEN or not settings.ADMIN_TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage"
    try:
        with httpx.Client(timeout=_HTTP_TIMEOUT) as client:
            client.post(
                url,
                json={"chat_id": settings.ADMIN_TELEGRAM_CHAT_ID, "text": text},
            )
    except httpx.HTTPError as e:
        print(f"Telegram notify failed: {e}")


def notify_new_user(username: str) -> None:
    _send(f"Создан новый пользователь - {username}")


def notify_new_wallet(username: str, wallet_name: str) -> None:
    _send(f"Пользователь {username} создал кошелек {wallet_name}")


def notify_new_expense(username: str, wallet_name: str, amount: int | float) -> None:
    _send(f"Пользователь {username} потратил {amount} с кошелька {wallet_name} ")

def notify_new_income(username: str, wallet_name: str, amount: int | float) -> None:
    _send(f"Пользователь {username} получил {amount} на счет {wallet_name}")
