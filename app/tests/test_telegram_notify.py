from unittest.mock import Mock

import app.service.telegram_notify as telegram_notify
from fastapi import status


class _FakeHttpClient:
    def __init__(self, calls: list):
        self._calls = calls

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def post(self, *args, **kwargs):
        self._calls.append((args, kwargs))


def test_notify_skipped_without_chat_id(monkeypatch):
    post_calls = []
    monkeypatch.setattr(telegram_notify.settings, "TELEGRAM_TOKEN", "fake-token")
    monkeypatch.setattr(telegram_notify.settings, "ADMIN_TELEGRAM_CHAT_ID", None)
    monkeypatch.setattr(
        telegram_notify.httpx,
        "Client",
        lambda **kwargs: _FakeHttpClient(post_calls),
    )

    def real_send(text: str) -> None:
        if not telegram_notify.settings.TELEGRAM_TOKEN or not telegram_notify.settings.ADMIN_TELEGRAM_CHAT_ID:
            return
        url = f"https://api.telegram.org/bot{telegram_notify.settings.TELEGRAM_TOKEN}/sendMessage"
        with telegram_notify.httpx.Client(timeout=telegram_notify._HTTP_TIMEOUT) as client:
            client.post(
                url,
                json={"chat_id": telegram_notify.settings.ADMIN_TELEGRAM_CHAT_ID, "text": text},
            )

    monkeypatch.setattr(telegram_notify, "_send", real_send)
    telegram_notify.notify_new_user("ivan")

    assert post_calls == []


def test_notify_new_user_on_register(client, monkeypatch):
    mock_send = Mock()
    monkeypatch.setattr(telegram_notify, "_send", mock_send)

    client.post("/auth/register", json={"username": "tg_user", "password": "123"})

    mock_send.assert_called_once_with("Создан новый пользователь - tg_user")


def test_notify_new_wallet_on_create(auth_client, monkeypatch):
    mock_send = Mock()
    monkeypatch.setattr(telegram_notify, "_send", mock_send)

    auth_client.post("/api/v1/wallets", json={"name": "tg_wallet", "initial_balance": 10})

    mock_send.assert_called_once_with("Пользователь testuser создал кошелек tg_wallet")


def test_notify_not_sent_on_failed_expense(auth_client, created_wallet, monkeypatch):
    mock_send = Mock()
    monkeypatch.setattr(telegram_notify, "_send", mock_send)

    response = auth_client.post(
        "/api/v1/operations/expense",
        json={"wallet_name": created_wallet["wallet"], "amount": 150},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    mock_send.assert_not_called()
