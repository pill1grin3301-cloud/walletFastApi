from fastapi import status


def test_add_income_success(auth_client, created_wallet):
    wallet_name = created_wallet["wallet"]
    response = auth_client.post(
        "/api/v1/operations/income",
        json={"wallet_name": wallet_name, "amount": 25, "description": "salary"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["type"] == "income"
    assert data["wallet_name"] == wallet_name
    assert data["amount"] == 25
    assert data["balance_after"] == 125
    assert "id" in data
    assert "created_at" in data


def test_add_income_updates_balance_correctly(auth_client, created_wallet):
    wallet_name = created_wallet["wallet"]
    response = auth_client.post(
        "/api/v1/operations/income",
        json={"wallet_name": wallet_name, "amount": 50},
    )
    assert response.status_code == status.HTTP_200_OK
    assert float(response.json()["balance_after"]) == 150


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
    assert data["type"] == "expense"
    assert data["wallet_name"] == wallet_name
    assert data["amount"] == 30
    assert data["balance_after"] == 70
    assert "id" in data
    assert "created_at" in data


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


def test_list_operations_after_income(auth_client, empty_wallet):
    wallet_name = empty_wallet["wallet"]
    auth_client.post(
        "/api/v1/operations/income",
        json={"wallet_name": wallet_name, "amount": 25, "description": "salary"},
    )
    response = auth_client.get("/api/v1/operations")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    item = data["items"][0]
    assert item["type"] == "income"
    assert item["amount"] == 25
    assert item["description"] == "salary"
    assert item["wallet_name"] == wallet_name
    assert item["balance_after"] == 25


def test_list_operations_filter_by_wallet(auth_client, empty_wallet):
    wallet_name = empty_wallet["wallet"]
    auth_client.post(
        "/api/v1/operations/income",
        json={"wallet_name": wallet_name, "amount": 10},
    )
    response = auth_client.get(f"/api/v1/operations?wallet_name={wallet_name}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 1

    response = auth_client.get("/api/v1/operations?wallet_name=missing_wallet")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_wallet_with_initial_balance_creates_operation(auth_client):
    wallet_name = "start_wallet"
    auth_client.post(
        "/api/v1/wallets",
        json={"name": wallet_name, "initial_balance": 50},
    )

    response = auth_client.get("/api/v1/operations")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1

    item = data["items"][0]
    assert item["type"] == "income"
    assert item["amount"] == 50
    assert item["description"] == "Initial Balance"
    assert item["balance_after"] == 50
    assert item["wallet_name"] == wallet_name
    assert "id" in item
    assert "created_at" in item


def test_create_wallet_zero_balance_no_operation(auth_client):
    auth_client.post(
        "/api/v1/wallets",
        json={"name": "empty_wallet_test", "initial_balance": 0},
    )

    response = auth_client.get("/api/v1/operations")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] == 0
    assert response.json()["items"] == []


def test_list_operations_without_token(client):
    response = client.get("/api/v1/operations")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
