from fastapi import status


def test_get_balance(auth_client):
    """Пытаемся получить баланс кошелька"""
    response = auth_client.get('/api/v1/balance/')
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), dict)


def test_get_all_wallets(auth_client):
    """Пытаемся получить список кошельков"""
    response = auth_client.get('/api/v1/')
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_rename_wallet(auth_client, created_wallet):
    """Пытаемся сменить имя на себя же, должна быть ошибка 409"""
    wallet_name = created_wallet['wallet']
    response = auth_client.patch(f'/api/v1/{wallet_name}', json={'new_name': wallet_name})
    assert response.status_code == status.HTTP_409_CONFLICT


def test_rename_wallet_to_name_already_exists(auth_client, created_wallet):
    """Пытаемся переименовать кошелек, на имя которое уже есть у другого кошелька - 409"""
    second_wallet = auth_client.post(
        url='/api/v1/wallets', 
        json={'name': 'second name wallet', 'initial_balance': 100}
    )
    wallet_name = created_wallet['wallet']
    response = auth_client.patch(url=f'/api/v1/{wallet_name}', json={'new_name': second_wallet.json()['wallet']})
    assert response.status_code == status.HTTP_409_CONFLICT


def test_create_wallet(auth_client):
    """Пытаемся создать кошелек - 201"""
    response = auth_client.post(
        url='/api/v1/wallets',
        json={'name': 'som name', 'initial_balance': 12},
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["wallet"] == "som name"


def test_create_wallet_without_name(auth_client):
    """Пытаемся создать кошелек с пустым именем - 422"""
    response = auth_client.post(
        '/api/v1/wallets',
        json={'name': "", 'initial_balance': 198})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_wallet_with_negative_balance(auth_client):
    """Пытаемся создать кошелек с отрицательным балансом - 422"""
    response = auth_client.post(
        '/api/v1/wallets',
        json={'name': "qwert", 'initial_balance': -123})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_wallet_with_long_name(auth_client):
    """Пытаемся создать кошелек с длинным именем - 422"""
    name = "zxc"*100
    response = auth_client.post(
        '/api/v1/wallets',
        json={'name': name, 'initial_balance': 123})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_delete_wallet(auth_client, created_wallet):
    """Пытаемся удалить кошелек 200 (особенность фронтенда), или 404"""
    wallet_name = created_wallet['wallet']
    response = auth_client.delete(f'/api/v1/{wallet_name}')
    # happy path
    assert response.status_code == status.HTTP_200_OK

    # double delete
    _response = auth_client.delete(f'/api/v1/{wallet_name}')
    assert _response.status_code == status.HTTP_404_NOT_FOUND
    
    # bad path
    bad_response = auth_client.delete('/api/v1/9999999')
    assert bad_response.status_code == status.HTTP_404_NOT_FOUND

def test_get_wallets_without_token(client):
    response = client.get("/api/v1/")
    assert response.status_code == 401


def test_get_wallets_with_token(auth_client):
    response = auth_client.get("/api/v1/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_wallet_without_token(client):
    response = client.post("/api/v1/wallets", json={"name": "my_wallet", "initial_balance": 100})
    assert response.status_code == 401

def test_user_sees_only_own_wallets(auth_client, test_user):
    """Пользователь видит только свои кошельки"""
    # Создаём кошелёк
    auth_client.post("/api/v1/wallets", json={"name": "my_wallet", "initial_balance": 100})
    
    # Получаем список кошельков
    response = auth_client.get("/api/v1/")
    wallets = response.json()
    
    # Проверяем, что все кошельки принадлежат этому пользователю
    for wallet in wallets:
        assert wallet["user_id"] == test_user["id"]


def test_user_cannot_see_other_wallet(auth_client, second_user_client):
    """Пользователь не может получить чужой кошелёк"""
    # Второй пользователь создаёт кошелёк
    response = second_user_client.post("/api/v1/wallets", json={"name": "other_wallet", "initial_balance": 200})
    other_wallet_name = response.json()["wallet"]
    
    # Первый пользователь пытается его получить
    response = auth_client.get(f"/api/v1/balance?wallet_name={other_wallet_name}")
    assert response.status_code == 404