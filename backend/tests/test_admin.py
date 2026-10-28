def user_id(client, headers):
    return client.get("/api/auth/me", headers=headers).json()["id"]


def set_role(client, headers, target_id, role):
    return client.put(f"/api/admin/users/{target_id}/role", json={"role": role}, headers=headers)


def test_new_users_get_the_user_role(client, auth_headers):
    assert client.get("/api/auth/me", headers=auth_headers).json()["role"] == "user"


def test_users_cannot_use_admin_endpoints(client, auth_headers):
    response = client.get("/api/admin/users", headers=auth_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Only admins can do this"


def test_admin_lists_users_with_project_counts(client, auth_headers, admin_headers, project):
    users = {u["username"]: u for u in client.get("/api/admin/users", headers=admin_headers).json()}
    assert users["alice"]["project_count"] == 1
    assert users["root"]["role"] == "admin"


def test_admin_sees_and_manages_every_project(client, auth_headers, admin_headers, project):
    projects = client.get("/api/projects", headers=admin_headers).json()
    assert [p["key"] for p in projects] == ["SB"]
    assert projects[0]["owner"]["username"] == "alice"

    issue = client.post(
        f"/api/projects/{project['id']}/issues", json={"title": "Fix login"}, headers=admin_headers
    )
    assert issue.status_code == 201
    assert client.delete(f"/api/projects/{project['id']}", headers=admin_headers).status_code == 204


def test_admin_can_promote_and_demote(client, auth_headers, admin_headers):
    alice = user_id(client, auth_headers)
    assert set_role(client, admin_headers, alice, "admin").json()["role"] == "admin"
    assert client.get("/api/admin/users", headers=auth_headers).status_code == 200
    assert set_role(client, admin_headers, alice, "user").json()["role"] == "user"


def test_invalid_role_is_rejected(client, auth_headers, admin_headers):
    response = set_role(client, admin_headers, user_id(client, auth_headers), "superuser")
    assert response.status_code == 422


def test_admin_cannot_change_own_role(client, admin_headers):
    response = set_role(client, admin_headers, user_id(client, admin_headers), "user")
    assert response.status_code == 400
    assert response.json()["detail"] == "You cannot change your own role"


def test_admin_deletes_user_and_their_projects(client, auth_headers, admin_headers, project):
    alice = user_id(client, auth_headers)
    assert client.delete(f"/api/admin/users/{alice}", headers=admin_headers).status_code == 204
    assert client.get("/api/projects", headers=admin_headers).json() == []
    assert client.get("/api/auth/me", headers=auth_headers).status_code == 401


def test_admin_cannot_delete_self(client, admin_headers):
    response = client.delete(f"/api/admin/users/{user_id(client, admin_headers)}", headers=admin_headers)
    assert response.status_code == 400


def test_deleting_unknown_user_returns_404(client, admin_headers):
    assert client.delete("/api/admin/users/999", headers=admin_headers).status_code == 404
