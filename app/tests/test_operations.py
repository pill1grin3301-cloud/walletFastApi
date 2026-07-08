from fastapi import status


def test_add_income_success(client, created_wallet):
    wallet_name = created_wallet["wallet"]
    response = client.post(
        "/api/v1/operations/income",
        json={"wallet_name": wallet_name, "amount": 25, "description": "salary"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Income added"
    assert data["wallet"] == wallet_name
    assert float(data["amount"]) == 25
    assert data["description"] == "salary"
    assert float(data["new_balance"]) == 125


def test_add_income_updates_balance_correctly(client, created_wallet):
    wallet_name = created_wallet["wallet"]
    response = client.post(
        "/api/v1/operations/income",
        json={"wallet_name": wallet_name, "amount": 50},
    )
    assert response.status_code == status.HTTP_200_OK
    assert float(response.json()["new_balance"]) == 150


def test_add_income_wallet_not_found(client):
    response = client.post(
        "/api/v1/operations/income",
        json={"wallet_name": "no_such_wallet", "amount": 10},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_add_income_invalid_amount_zero(client, created_wallet):
    response = client.post(
        "/api/v1/operations/income",
        json={"wallet_name": created_wallet["wallet"], "amount": 0},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_add_income_invalid_amount_negative(client, created_wallet):
    response = client.post(
        "/api/v1/operations/income",
        json={"wallet_name": created_wallet["wallet"], "amount": -5},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_add_expense_success(client, created_wallet):
    wallet_name = created_wallet["wallet"]
    response = client.post(
        "/api/v1/operations/expense",
        json={"wallet_name": wallet_name, "amount": 30, "description": "food"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Expense added"
    assert data["wallet"] == wallet_name
    assert float(data["amount"]) == 30
    assert data["description"] == "food"
    assert float(data["new_balance"]) == 70


def test_add_expense_insufficient_funds(client, created_wallet):
    wallet_name = created_wallet["wallet"]
    response = client.post(
        "/api/v1/operations/expense",
        json={"wallet_name": wallet_name, "amount": 150},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Insufficient funds" in response.json()["detail"]


def test_add_expense_wallet_not_found(client):
    response = client.post(
        "/api/v1/operations/expense",
        json={"wallet_name": "no_such_wallet", "amount": 10},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_add_expense_invalid_amount(client, created_wallet):
    response = client.post(
        "/api/v1/operations/expense",
        json={"wallet_name": created_wallet["wallet"], "amount": 0},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_add_expense_updates_balance_correctly(client, empty_wallet):
    wallet_name = empty_wallet["wallet"]
    client.post(
        "/api/v1/operations/income",
        json={"wallet_name": wallet_name, "amount": 100},
    )
    response = client.post(
        "/api/v1/operations/expense",
        json={"wallet_name": wallet_name, "amount": 40},
    )
    assert response.status_code == status.HTTP_200_OK
    assert float(response.json()["new_balance"]) == 60
