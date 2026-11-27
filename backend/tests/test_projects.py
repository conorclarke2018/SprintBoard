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


def test_users_can_see_approved_projects_but_not_others_requests(client, auth_headers, project):
    pending = client.post(
        "/api/projects", json={"name": "Secret", "key": "SEC"}, headers=auth_headers
    ).json()
    bob = login_headers(client, "bob")

    visible = client.get("/api/projects", headers=bob).json()
    assert [p["key"] for p in visible] == ["SB"]
    assert client.get(f"/api/projects/{project['id']}", headers=bob).status_code == 200
    assert client.get(f"/api/projects/{pending['id']}", headers=bob).status_code == 404


def test_users_cannot_edit_other_peoples_projects(client, auth_headers, project):
    bob = login_headers(client, "bob")
    response = client.put(
        f"/api/projects/{project['id']}", json={"name": "Taken over"}, headers=bob
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "You can only change your own projects"


def test_update_project(client, auth_headers, project):
    response = client.put(
        f"/api/projects/{project['id']}",
        json={"name": "Renamed", "description": "New text"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Renamed"
    assert response.json()["key"] == "SB"


def test_admin_delete_project_also_deletes_its_issues(client, auth_headers, admin_headers, project):
    issue = client.post(
        f"/api/projects/{project['id']}/issues", json={"title": "Login"}, headers=auth_headers
    ).json()

    response = client.delete(f"/api/projects/{project['id']}", headers=admin_headers)

    assert response.status_code == 204
    assert client.get(f"/api/projects/{project['id']}", headers=auth_headers).status_code == 404
    assert client.get(f"/api/issues/{issue['id']}", headers=auth_headers).status_code == 404


def test_regular_user_cannot_delete_own_project(client, auth_headers, project):
    response = client.delete(f"/api/projects/{project['id']}", headers=auth_headers)
    assert response.status_code == 403
    assert client.get(f"/api/projects/{project['id']}", headers=auth_headers).status_code == 200


def test_projects_require_login(client):
    assert client.get("/api/projects").status_code == 401
