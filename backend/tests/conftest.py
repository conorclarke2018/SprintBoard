"""Test fixtures: a fresh in-memory database and API client for every test."""

from collections.abc import Iterator

import bcrypt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Project
from app.models.enums import ProjectStatus

test_engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSession = sessionmaker(bind=test_engine, autoflush=False)

PASSWORD = "password123"


@pytest.fixture(autouse=True)
def fast_password_hashing(monkeypatch: pytest.MonkeyPatch) -> None:
    """bcrypt is slow on purpose; use its cheapest setting in tests only."""
    real_gensalt = bcrypt.gensalt
    monkeypatch.setattr(bcrypt, "gensalt", lambda: real_gensalt(rounds=4))


@pytest.fixture
def db() -> Iterator[Session]:
    Base.metadata.create_all(test_engine)
    session = TestingSession()
    yield session
    session.close()
    Base.metadata.drop_all(test_engine)


@pytest.fixture
def bare_client(db: Session) -> Iterator[TestClient]:
    """An API client on a completely empty database (no accounts yet)."""
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def client(bare_client: TestClient) -> TestClient:
    """An API client where 'root' has already registered, so 'root' is the admin."""
    bare_client.post("/api/auth/register", json={"username": "root", "password": PASSWORD})
    return bare_client


def _token(client: TestClient, username: str) -> str:
    response = client.post("/api/auth/login", json={"username": username, "password": PASSWORD})
    return response.json()["access_token"]


def login_headers(client: TestClient, username: str) -> dict[str, str]:
    """Register a user (if needed), have 'root' approve them, log in and return the auth header."""
    response = client.post("/api/auth/register", json={"username": username, "password": PASSWORD})
    if response.status_code == 201 and not response.json()["is_approved"]:
        root = {"Authorization": f"Bearer {_token(client, 'root')}"}
        client.post(f"/api/admin/users/{response.json()['id']}/approve", headers=root)
    return {"Authorization": f"Bearer {_token(client, username)}"}


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    return login_headers(client, "alice")


@pytest.fixture
def admin_headers(client: TestClient) -> dict[str, str]:
    return {"Authorization": f"Bearer {_token(client, 'root')}"}


def create_approved_project(
    client: TestClient, db: Session, headers: dict[str, str], name: str, key: str
) -> dict:
    """Request a project as a normal user, then approve it directly in the database."""
    response = client.post("/api/projects", json={"name": name, "key": key}, headers=headers)
    project = db.get(Project, response.json()["id"])
    project.status = ProjectStatus.APPROVED
    db.commit()
    return {**response.json(), "status": "approved"}


@pytest.fixture
def project(client: TestClient, db: Session, auth_headers: dict[str, str]) -> dict:
    return create_approved_project(client, db, auth_headers, "SprintBoard", "SB")


@pytest.fixture
def sprint(client: TestClient, auth_headers: dict[str, str], project: dict) -> dict:
    response = client.post(
        f"/api/projects/{project['id']}/sprints",
        json={"name": "Sprint 1", "start_date": "2026-11-02", "end_date": "2026-11-15"},
        headers=auth_headers,
    )
    return response.json()
