from fastapi import status


def test_get_balance(client):
    """Пытаемся получить общий баланс"""
    response = client.get("/api/v1/balance")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), dict)


def test_get_all_wallets(client):
    """Пытаемся получить список кошельков"""
    response = client.get("/api/v1/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_rename_wallet(client, created_wallet):
    """Пытаемся сменить имя на себя же, должна быть ошибка 409"""
    wallet_name = created_wallet["wallet"]
    response = client.patch(f"/api/v1/{wallet_name}", json={"new_name": wallet_name})
    assert response.status_code == status.HTTP_409_CONFLICT


def test_rename_wallet_to_name_already_exists(client, created_wallet):
    """Переименование на имя существующего кошелька — 409"""
    second_wallet = client.post(
        url="/api/v1/wallets",
        json={"name": "second name wallet", "initial_balance": 100},
    )
    wallet_name = created_wallet["wallet"]
    response = client.patch(
        url=f"/api/v1/{wallet_name}",
        json={"new_name": second_wallet.json()["wallet"]},
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_create_wallet(client):
    """Создание кошелька — 201"""
    response = client.post(
        url="/api/v1/wallets",
        json={"name": "som name", "initial_balance": 12},
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["wallet"] == "som name"
    assert float(response.json()["balance"]) == 12


def test_create_wallet_without_name(client):
    """Создание кошелька с пустым именем — 422"""
    response = client.post(
        "/api/v1/wallets",
        json={"name": "", "initial_balance": 198},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_wallet_with_negative_balance(client):
    """Создание кошелька с отрицательным балансом — 422"""
    response = client.post(
        "/api/v1/wallets",
        json={"name": "qwert", "initial_balance": -123},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_wallet_with_long_name(client):
    """Создание кошелька с длинным именем — 422"""
    name = "zxc" * 100
    response = client.post(
        "/api/v1/wallets",
        json={"name": name, "initial_balance": 123},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_delete_wallet(client, created_wallet):
    """Удаление кошелька — 200, повторное удаление — 404"""
    wallet_name = created_wallet["wallet"]
    response = client.delete(f"/api/v1/{wallet_name}")
    assert response.status_code == status.HTTP_200_OK

    response = client.delete(f"/api/v1/{wallet_name}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = client.delete("/api/v1/9999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_rename_wallet_success(client, created_wallet):
    wallet_name = created_wallet["wallet"]
    new_name = "renamed_wallet"
    response = client.patch(f"/api/v1/{wallet_name}", json={"new_name": new_name})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == new_name


def test_get_balance_specific_wallet(client, created_wallet):
    wallet_name = created_wallet["wallet"]
    response = client.get(f"/api/v1/balance?wallet_name={wallet_name}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["wallet"] == wallet_name
    assert float(data["balance"]) == 100


def test_get_balance_total(client, created_wallet):
    client.post("/api/v1/wallets", json={"name": "second_wallet", "initial_balance": 50})
    response = client.get("/api/v1/balance")
    assert response.status_code == status.HTTP_200_OK
    assert float(response.json()["total_balance"]) == 150


def test_create_wallet_duplicate_name(client, created_wallet):
    wallet_name = created_wallet["wallet"]
    response = client.post(
        "/api/v1/wallets",
        json={"name": wallet_name, "initial_balance": 10},
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_rename_wallet_not_found(client):
    response = client.patch("/api/v1/missing_wallet", json={"new_name": "new_name"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_balance_wallet_not_found(client):
    response = client.get("/api/v1/balance?wallet_name=missing_wallet")
    assert response.status_code == status.HTTP_404_NOT_FOUND
