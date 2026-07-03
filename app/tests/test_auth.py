def test_register_success(client):
    response = client.post("/auth/register", json={"username": "newuser", "password": "123"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_register_duplicate(client, test_user):
    response = client.post("/auth/register", json={"username": test_user["username"], "password": "123"})
    assert response.status_code == 409


def test_login_success(client, test_user):
    response = client.post("/auth/login", json={"username": test_user['username'], "password": "testpass"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_nonexistent_user(client):
    response = client.post("/auth/login", json={"username": "@@@@@", "password": "testpass"})
    assert response.status_code == 401


def test_login_wrong_password(client, test_user):
    response = client.post("/auth/login", json={"username": test_user['username'], "password": "wrong"})
    assert response.status_code == 401


def test_delete_user(auth_client):
    response = auth_client.delete('/auth/delete')
    assert response.status_code == 204

    response2 = auth_client.delete('/auth/delete')
    assert response2.status_code == 401


def test_delete_unauth_user(client):
    response = client.delete('/auth/delete')
    assert response.status_code == 401


def test_delete_with_invalid_token(client):
    client.headers = {"Authorization": "Bearer invalid.token.here"}
    response = client.delete('/auth/delete')
    assert response.status_code == 401


def test_access_after_deletion(auth_client, test_user):
    # Удалить пользователя
    auth_client.delete('/auth/delete')
    
    # Попробовать получить кошельки
    response = auth_client.get('/api/v1/')
    assert response.status_code == 401


def test_register_invalid_short_password(client):
    response = client.post("/auth/register", json={"username": "shortpass", "password": "12"})
    assert response.status_code == 422


def test_register_returns_valid_jwt(client):
    response = client.post("/auth/register", json={"username": "jwtuser", "password": "123"})
    assert response.status_code == 200

    from jose import jwt
    from app.service.auth import SECRET_KEY, ALGORITHM

    token = response.json()["access_token"]
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload.get("sub") is not None
    assert payload.get("exp") is not None
