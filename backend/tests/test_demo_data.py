from sqlalchemy import func, select

from app.demo_data import DEMO_PASSWORD, create_demo_data
from app.models import Issue, Project, Sprint, User

MINIMUM_RECORDS = 10


def count(db, model):
    return db.scalar(select(func.count()).select_from(model))


def test_demo_data_has_at_least_ten_records_per_table(client, db):
    assert create_demo_data(db) is True
    for model in (User, Project, Sprint, Issue):
        assert count(db, model) >= MINIMUM_RECORDS, model.__tablename__


def test_demo_data_is_only_added_once(client, db):
    create_demo_data(db)
    projects = count(db, Project)
    assert create_demo_data(db) is False
    assert count(db, Project) == projects


def test_demo_data_needs_an_admin(bare_client, db):
    assert create_demo_data(db) is False
    assert count(db, User) == 0


def test_demo_users_can_log_in(client, db):
    create_demo_data(db)
    response = client.post("/api/auth/login", json={"username": "alice", "password": DEMO_PASSWORD})
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "user"


def test_demo_user_sees_approved_projects_read_only(client, db):
    create_demo_data(db)
    token = client.post(
        "/api/auth/login", json={"username": "ben", "password": DEMO_PASSWORD}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    keys = {project["key"] for project in client.get("/api/projects", headers=headers).json()}
    assert {"SB", "HD", "ASSET"} <= keys
    assert "ONB" not in keys  # hannah's pending request stays private
