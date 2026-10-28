import logging

from tests.conftest import PASSWORD, login_headers


def register(client, username="alice", password=PASSWORD):
    return client.post("/api/auth/register", json={"username": username, "password": password})


def test_register_creates_user_without_exposing_password(client):
    response = register(client)
    assert response.status_code == 201
    assert response.json()["username"] == "alice"
    assert "password" not in response.text


def test_username_is_stored_in_lowercase(client):
    assert register(client, username="  Alice ").json()["username"] == "alice"


def test_duplicate_username_is_rejected(client):
    register(client)
    response = register(client, username="ALICE")
    assert response.status_code == 409
    assert response.json()["detail"] == "That username is already taken"


def test_short_password_is_rejected(client):
    response = register(client, password="short")
    assert response.status_code == 422
    assert response.json()["detail"].startswith("Password:")


def test_username_with_symbols_is_rejected(client):
    response = register(client, username="bad name!")
    assert response.status_code == 422
    assert "letters, numbers and underscores" in response.json()["detail"]


def test_login_returns_token_and_user(client):
    login_headers(client, "alice")
    response = client.post("/api/auth/login", json={"username": "alice", "password": PASSWORD})
    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["user"]["username"] == "alice"


def test_wrong_password_is_rejected_and_logged(client, caplog):
    register(client)
    with caplog.at_level(logging.WARNING):
        response = client.post(
            "/api/auth/login", json={"username": "alice", "password": "wrong-password"}
        )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"
    assert "Failed login attempt for username 'alice'" in caplog.text
    assert "wrong-password" not in caplog.text


def test_me_returns_current_user(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "alice"


def test_me_requires_login(client):
    assert client.get("/api/auth/me").status_code == 401


def test_me_rejects_invalid_token(client):
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-token"})
    assert response.status_code == 401
