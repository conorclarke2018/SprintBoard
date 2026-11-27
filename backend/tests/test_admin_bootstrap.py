import logging

from sqlalchemy import select

from app.models import User
from app.services.user_service import ensure_admin_account
from tests.conftest import PASSWORD


def login(client, username, password):
    return client.post("/api/auth/login", json={"username": username, "password": password})


def test_creates_admin_on_empty_database(db, bare_client):
    ensure_admin_account(db, "Marker", "marker-pass-1")
    response = login(bare_client, "marker", "marker-pass-1")
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "admin"


def test_running_twice_does_not_duplicate(db):
    ensure_admin_account(db, "marker", "marker-pass-1")
    ensure_admin_account(db, "marker", "marker-pass-1")
    assert len(db.scalars(select(User).where(User.username == "marker")).all()) == 1


def test_existing_account_is_promoted_and_password_updated(db, client):
    client.post("/api/auth/register", json={"username": "sam", "password": PASSWORD})
    ensure_admin_account(db, "sam", "new-password-9")
    assert login(client, "sam", PASSWORD).status_code == 401
    response = login(client, "sam", "new-password-9")
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "admin"


def test_later_sign_ups_are_normal_users(db, bare_client):
    ensure_admin_account(db, "marker", "marker-pass-1")
    body = bare_client.post(
        "/api/auth/register", json={"username": "visitor", "password": PASSWORD}
    ).json()
    assert body["role"] == "user"
    assert body["is_approved"] is False


def test_invalid_settings_are_logged_and_skipped(db, caplog):
    with caplog.at_level(logging.ERROR):
        assert ensure_admin_account(db, "marker", "short") is None
    assert "ADMIN_USERNAME/ADMIN_PASSWORD are invalid" in caplog.text
    assert "short" not in caplog.text  # the password itself is never logged
    assert db.scalar(select(User)) is None
