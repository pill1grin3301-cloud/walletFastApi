import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:admin@wallet_test_db:5432/test_db",
)

test_engine = create_engine(TEST_DATABASE_URL, connect_args={"connect_timeout": 10})


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Создаём таблицы в test_db перед тестами"""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    """Изолированная сессия для каждого теста"""
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
def created_wallet(client):
    response = client.post(
        "/api/v1/wallets",
        json={"name": "unique_name", "initial_balance": 100},
    )
    return response.json()


@pytest.fixture
def empty_wallet(client):
    response = client.post(
        "/api/v1/wallets",
        json={"name": "empty_wallet", "initial_balance": 0},
    )
    return response.json()
