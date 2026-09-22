"""Тесты модуля авторизации."""


def test_register_user(client):
    """Проверяет регистрацию нового пользователя."""
    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "secret123",
        "role": "executor",
    })
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_login_success(client):
    """Проверяет успешный вход и получение JWT-токена."""
    client.post("/auth/register", json={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "secret123",
        "role": "executor",
    })
    response = client.post("/auth/login", data={
        "username": "loginuser",
        "password": "secret123",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_failure(client):
    """Проверяет отказ во входе с неверными учётными данными."""
    response = client.post("/auth/login", data={
        "username": "nonexistent",
        "password": "wrong",
    })
    assert response.status_code == 401
