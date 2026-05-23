
from fastapi import status

def test_get_balance(client):
    response = client.get('/api/v1/balance/')
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), dict)


def test_get_all_wallets(client):
    response = client.get('/api/v1/')
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_rename_wallet(client, created_wallet):
    """Пытаемся сменить имя на себя же, должна быть ошибка 409"""
    wallet_name = created_wallet['wallet']
    response = client.patch(f'/api/v1/{wallet_name}', json={'new_name': wallet_name})
    assert response.status_code == status.HTTP_409_CONFLICT


def test_rename_wallet_to_name_already_exists(client, created_wallet):
    """Пытаемся переименовать кошелек, на имя которое уже есть у другого кошелька - 409"""
    second_wallet = client.post(
        url='/api/v1/wallets', 
        json={'name': 'second name wallet', 'initial_balance': 100}
    )
    wallet_name = created_wallet['wallet']
    response = client.patch(url=f'/api/v1/{wallet_name}', json={'new_name': second_wallet.json()['wallet']})
    assert response.status_code == status.HTTP_409_CONFLICT


def test_create_wallet(client):
    response = client.post(
        url='/api/v1/wallets', 
        json={'name': 'som name', 'initial_balance': 12}
    )
    assert response.status_code == status.HTTP_201_CREATED


def test_create_wallet_without_name(client):
    response = client.post(
        '/api/v1/wallets',
        json={'name': "", 'initial_balance': 198})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_wallet_with_negative_balance(client):
    response = client.post(
        '/api/v1/wallets',
        json={'name': "qwert", 'initial_balance': -123})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_wallet_with_long_name(client):
    name = "zxc"*100
    response = client.post(
        '/api/v1/wallets',
        json={'name': name, 'initial_balance': 123})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT





def test_delete_wallet(client, created_wallet):
    wallet_name = created_wallet['wallet']
    response = client.delete(f'/api/v1/{wallet_name}')
    # happy path
    assert response.status_code == status.HTTP_200_OK

    # double delete
    _response = client.delete(f'/api/v1/{wallet_name}')
    assert _response.status_code == status.HTTP_404_NOT_FOUND
    
    # bad path
    bad_response = client.delete('/api/v1/9999999')
    assert bad_response.status_code == status.HTTP_404_NOT_FOUND
