import logging

from tests.conftest import PASSWORD


def register(client, username):
    return client.post("/api/auth/register", json={"username": username, "password": PASSWORD})


def login(client, username):
    return client.post("/api/auth/login", json={"username": username, "password": PASSWORD})


def approve(client, headers, user):
    return client.post(f"/api/admin/users/{user['id']}/approve", headers=headers)


def test_first_account_becomes_approved_admin(bare_client):
    body = register(bare_client, "founder").json()
    assert body["role"] == "admin"
    assert body["is_approved"] is True
    assert login(bare_client, "founder").status_code == 200


def test_later_accounts_wait_for_approval(client):
    body = register(client, "newbie").json()
    assert body["role"] == "user"
    assert body["is_approved"] is False


def test_unapproved_user_cannot_log_in(client, caplog):
    register(client, "newbie")
    with caplog.at_level(logging.WARNING):
        response = login(client, "newbie")
    assert response.status_code == 403
    assert response.json()["detail"] == "Your account is waiting for an admin to approve it"
    assert "Login blocked for unapproved user 'newbie'" in caplog.text


def test_wrong_password_is_checked_before_approval(client):
    register(client, "newbie")
    response = client.post("/api/auth/login", json={"username": "newbie", "password": "wrong-pass"})
    assert response.status_code == 401


def test_admin_sees_pending_accounts(client, admin_headers):
    register(client, "newbie")
    users = {u["username"]: u for u in client.get("/api/admin/users", headers=admin_headers).json()}
    assert users["newbie"]["is_approved"] is False
    assert users["root"]["is_approved"] is True


def test_admin_approves_account_and_user_can_log_in(client, admin_headers):
    user = register(client, "newbie").json()
    response = approve(client, admin_headers, user)
    assert response.status_code == 200
    assert response.json()["is_approved"] is True
    assert login(client, "newbie").status_code == 200


def test_account_can_only_be_approved_once(client, admin_headers):
    user = register(client, "newbie").json()
    approve(client, admin_headers, user)
    response = approve(client, admin_headers, user)
    assert response.status_code == 400
    assert response.json()["detail"] == "This account is already approved"


def test_users_cannot_approve_accounts(client, auth_headers):
    user = register(client, "newbie").json()
    assert approve(client, auth_headers, user).status_code == 403


def test_admin_rejects_account_by_deleting_it(client, admin_headers):
    user = register(client, "newbie").json()
    assert client.delete(f"/api/admin/users/{user['id']}", headers=admin_headers).status_code == 204
    assert register(client, "newbie").status_code == 201


def test_unapproved_users_cannot_be_assigned(client, auth_headers):
    register(client, "newbie")
    names = [u["username"] for u in client.get("/api/users", headers=auth_headers).json()]
    assert "newbie" not in names
    assert "alice" in names
