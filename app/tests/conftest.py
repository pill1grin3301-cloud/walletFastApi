import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL must be set to run tests")

test_engine = create_engine(TEST_DATABASE_URL, connect_args={"connect_timeout": 10})


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def disable_telegram_notify(monkeypatch):
    monkeypatch.setattr("app.service.telegram_notify._send", lambda text: None)


@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    yield session

    transaction.rollback()
    session.close()
    connection.close()
    app.dependency_overrides.clear()


@pytest.fixture
def client(db_session):
    return TestClient(app)


@pytest.fixture
def created_wallet(auth_client):
    response = auth_client.post(
        "/api/v1/wallets",
        json={"name": "unique_name", "initial_balance": 100},
    )
    return response.json()


@pytest.fixture
def empty_wallet(auth_client):
    response = auth_client.post(
        "/api/v1/wallets",
        json={"name": "unique_name", "initial_balance": 0},
    )
    return response.json()


@pytest.fixture
def test_user(client):
    username = "testuser"
    password = "testpass"

    client.post("/auth/register", json={"username": username, "password": password})
    response = client.post("/auth/login", json={"username": username, "password": password})
    token = response.json()["access_token"]

    from jose import jwt

    from app.service.auth import ALGORITHM, SECRET_KEY

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get("sub")

    return {"username": username, "token": token, "id": user_id}


@pytest.fixture
def auth_client(test_user):
    client = TestClient(app)
    client.headers = {"Authorization": f"Bearer {test_user['token']}"}
    return client


@pytest.fixture
def second_user_client(second_user):
    client = TestClient(app)
    client.headers = {"Authorization": f"Bearer {second_user['token']}"}
    return client


@pytest.fixture
def second_user(client):
    username = "rofl"
    password = "nerofl"

    client.post("/auth/register", json={"username": username, "password": password})
    response = client.post("/auth/login", json={"username": username, "password": password})
    token = response.json()["access_token"]

    return {"username": username, "token": token}
