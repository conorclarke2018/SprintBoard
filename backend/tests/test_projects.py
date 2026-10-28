import pytest

from tests.conftest import login_headers


def test_create_project(client, auth_headers):
    response = client.post(
        "/api/projects",
        json={"name": "Website", "key": "web", "description": "  "},
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["key"] == "WEB"
    assert body["description"] is None
    assert body["issue_count"] == 0
    assert body["status"] == "pending"


@pytest.mark.parametrize("key", ["S", "TOOLONG", "S1", "S-B"])
def test_invalid_project_key_is_rejected(client, auth_headers, key):
    response = client.post(
        "/api/projects", json={"name": "Website", "key": key}, headers=auth_headers
    )
    assert response.status_code == 422
    assert "Key must be 2 to 5 letters" in response.json()["detail"]


def test_duplicate_project_key_is_rejected(client, auth_headers, project):
    response = client.post(
        "/api/projects", json={"name": "Another", "key": "SB"}, headers=auth_headers
    )
    assert response.status_code == 409


def test_short_project_name_is_rejected(client, auth_headers):
    response = client.post("/api/projects", json={"name": "AB", "key": "AB"}, headers=auth_headers)
    assert response.status_code == 422
    assert response.json()["detail"].startswith("Name:")


def test_users_only_see_their_own_projects(client, auth_headers, project):
    bob = login_headers(client, "bob")
    assert client.get("/api/projects", headers=bob).json() == []
    assert client.get(f"/api/projects/{project['id']}", headers=bob).status_code == 404
    assert len(client.get("/api/projects", headers=auth_headers).json()) == 1


def test_update_project(client, auth_headers, project):
    response = client.put(
        f"/api/projects/{project['id']}",
        json={"name": "Renamed", "description": "New text"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Renamed"
    assert response.json()["key"] == "SB"


def test_delete_project_also_deletes_its_issues(client, auth_headers, project):
    issue = client.post(
        f"/api/projects/{project['id']}/issues", json={"title": "Login"}, headers=auth_headers
    ).json()

    response = client.delete(f"/api/projects/{project['id']}", headers=auth_headers)

    assert response.status_code == 204
    assert client.get(f"/api/projects/{project['id']}", headers=auth_headers).status_code == 404
    assert client.get(f"/api/issues/{issue['id']}", headers=auth_headers).status_code == 404


def test_projects_require_login(client):
    assert client.get("/api/projects").status_code == 401
