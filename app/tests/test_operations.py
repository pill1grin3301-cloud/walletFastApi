from fastapi import status


def test_add_income_success(auth_client, created_wallet):
    wallet_name = created_wallet["wallet"]
    response = auth_client.post(
        "/api/v1/operations/income",
        json={"wallet_name": wallet_name, "amount": 25, "description": "salary"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Income added"
    assert data["wallet"] == wallet_name
    assert data["amount"] == 25
    assert data["description"] == "salary"


def test_add_income_updates_balance_correctly(auth_client, created_wallet):
    wallet_name = created_wallet["wallet"]
    response = auth_client.post(
        "/api/v1/operations/income",
        json={"wallet_name": wallet_name, "amount": 50},
    )
    assert response.status_code == status.HTTP_200_OK
    assert float(response.json()["new_balance"]) == 150


def test_add_income_wallet_not_found(auth_client):
    response = auth_client.post(
        "/api/v1/operations/income",
        json={"wallet_name": "no_such_wallet", "amount": 10},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_add_income_without_token(client):
    response = client.post(
        "/api/v1/operations/income",
        json={"wallet_name": "any", "amount": 10},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_add_income_invalid_amount_zero(auth_client, created_wallet):
    response = auth_client.post(
        "/api/v1/operations/income",
        json={"wallet_name": created_wallet["wallet"], "amount": 0},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_add_income_invalid_amount_negative(auth_client, created_wallet):
    response = auth_client.post(
        "/api/v1/operations/income",
        json={"wallet_name": created_wallet["wallet"], "amount": -5},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_add_income_other_user_wallet(auth_client, second_user_client):
    response = second_user_client.post(
        "/api/v1/wallets",
        json={"name": "other_income_wallet", "initial_balance": 100},
    )
    other_wallet_name = response.json()["wallet"]

    response = auth_client.post(
        "/api/v1/operations/income",
        json={"wallet_name": other_wallet_name, "amount": 10},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_add_expense_success(auth_client, created_wallet):
    wallet_name = created_wallet["wallet"]
    response = auth_client.post(
        "/api/v1/operations/expense",
        json={"wallet_name": wallet_name, "amount": 30, "description": "food"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Expense added"
    assert data["wallet"] == wallet_name
    assert data["amount"] == 30
    assert float(data["new_balance"]) == 70


def test_add_expense_insufficient_funds(auth_client, created_wallet):
    wallet_name = created_wallet["wallet"]
    response = auth_client.post(
        "/api/v1/operations/expense",
        json={"wallet_name": wallet_name, "amount": 150},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Insufficient funds" in response.json()["detail"]


def test_add_expense_wallet_not_found(auth_client):
    response = auth_client.post(
        "/api/v1/operations/expense",
        json={"wallet_name": "no_such_wallet", "amount": 10},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_add_expense_without_token(client):
    response = client.post(
        "/api/v1/operations/expense",
        json={"wallet_name": "any", "amount": 10},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_add_expense_invalid_amount(auth_client, created_wallet):
    response = auth_client.post(
        "/api/v1/operations/expense",
        json={"wallet_name": created_wallet["wallet"], "amount": 0},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
