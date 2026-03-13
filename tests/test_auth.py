from .conftest import test_data


# /api/auth/register ---------------------------

def test_register_success(test_client):
    """Тест корректной регистрации"""
    response = test_client.post("/api/auth/register", json=test_data)
    assert response.status_code == 200
    assert response.status_code == 200
    assert response.json()["detail"] == "ok"


def test_register_duplicate_username(test_client):
    """Тест регистрации с занятым username"""
    bad_payload = {
        "username": test_data["username"],
        "password": "StrongPass123"
    }
    test_client.post("/api/auth/register", json=test_data)
    response = test_client.post("/api/auth/register", json=bad_payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"


def test_register_short_password(test_client):
    """Тест регистрации с коротким паролем"""
    bad_payload = {
        "username": test_data["username"],
        "password": "1!"
    }
    response = test_client.post("/api/auth/register", json=bad_payload)
    assert response.status_code == 422
    detail_msgs = [d["msg"] for d in response.json()["detail"]]
    assert "String should have at least 10 characters" in detail_msgs


# /api/auth/login ---------------------------

def test_login_success(test_client):
    """Тест успешной авторизации"""
    test_client.post("/api/auth/register", json=test_data)
    response = test_client.post("/api/auth/login", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_username_not_found(test_client):
    """Тест авторизации с несуществующим username"""
    test_client.post("/api/auth/register", json=test_data)
    bad_payload = {
        "username": "who am i",
        "password": "a"
    }
    response = test_client.post("/api/auth/login", json=bad_payload)
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Incorrect username or password"


def test_login_password_invalid(test_client):
    """Тест авторизации с невалидным паролем"""
    test_client.post("/api/auth/register", json=test_data)
    bad_payload = {
        "username": test_data["username"],
        "password": "a"
    }
    response = test_client.post("/api/auth/login", json=bad_payload)
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Incorrect username or password"


def test_double_login_different_keys(test_client):
    """Тест повторный логин возвращает не одинаковые ключи"""
    test_client.post("/api/auth/register", json=test_data)
    response = test_client.post("/api/auth/login", json=test_data)
    assert response.status_code == 200
    data = response.json()
    old_access_token = data["access_token"]
    old_refresh_token = data["refresh_token"]
    response = test_client.post("/api/auth/login", json=test_data)
    assert response.status_code == 200
    data = response.json()
    access_token = data["access_token"]
    refresh_token = data["refresh_token"]
    assert access_token != old_access_token
    assert refresh_token != old_refresh_token


# /api/auth/refresh ---------------------------

def test_refresh_success(test_client):
    """Тест успешного обновления токенов и блокировки старого refresh токена"""
    response = test_client.post("/api/auth/register", json=test_data)
    assert response.status_code == 200
    response = test_client.post("/api/auth/login", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    old_refresh_token = data["refresh_token"]
    payload = {"refresh_token": old_refresh_token}
    response = test_client.post("/api/auth/refresh", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    response = test_client.post("/api/auth/refresh", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Token revoked"


# /api/auth/logout ---------------------------

def test_logout(test_client):
    """Тест выхода и повторного выхода"""
    response = test_client.post("/api/auth/register", json=test_data)
    assert response.status_code == 200
    response = test_client.post("/api/auth/login", json=test_data)
    assert response.status_code == 200
    data = response.json()
    access_token = data["access_token"]
    response = test_client.post("/api/auth/logout", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["detail"] == "Logged out successfully"
    response = test_client.post("/api/auth/logout", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Token revoked"
