import pytest

from tests.conftest import create_approved_project, login_headers


def create_issue(client, headers, project, **fields):
    body = {"title": "Build login page", **fields}
    return client.post(f"/api/projects/{project['id']}/issues", json=body, headers=headers)


def full_update(issue, **changes):
    """Build a PUT body from an existing issue, with some fields changed."""
    body = {
        "title": issue["title"],
        "description": issue["description"],
        "type": issue["type"],
        "priority": issue["priority"],
        "story_points": issue["story_points"],
        "assignee_id": issue["assignee"]["id"] if issue["assignee"] else None,
        "sprint_id": issue["sprint_id"],
        "status": issue["status"],
    }
    return {**body, **changes}


def test_create_issue_with_defaults(client, auth_headers, project):
    response = create_issue(client, auth_headers, project)
    assert response.status_code == 201
    body = response.json()
    assert body["key"] == "SB-1"
    assert body["status"] == "todo"
    assert body["type"] == "story"
    assert body["priority"] == "medium"
    assert body["sprint_id"] is None


def test_issue_numbers_increase_per_project(client, auth_headers, project):
    create_issue(client, auth_headers, project)
    assert create_issue(client, auth_headers, project).json()["key"] == "SB-2"


@pytest.mark.parametrize(
    "fields, field_name",
    [
        ({"title": "ab"}, "Title"),
        ({"title": "x" * 121}, "Title"),
        ({"story_points": 4}, "Story points"),
        ({"type": "epic"}, "Type"),
        ({"priority": "urgent"}, "Priority"),
    ],
)
def test_invalid_issue_fields_are_rejected(client, auth_headers, project, fields, field_name):
    response = create_issue(client, auth_headers, project, **fields)
    assert response.status_code == 422
    assert response.json()["detail"].startswith(f"{field_name}:")


def test_assign_issue_to_user(client, auth_headers, project):
    me = client.get("/api/auth/me", headers=auth_headers).json()
    response = create_issue(client, auth_headers, project, assignee_id=me["id"])
    assert response.json()["assignee"]["username"] == "alice"


def test_unknown_assignee_is_rejected(client, auth_headers, project):
    response = create_issue(client, auth_headers, project, assignee_id=999)
    assert response.status_code == 400


def test_update_issue_status_and_sprint(client, auth_headers, project, sprint):
    issue = create_issue(client, auth_headers, project).json()
    response = client.put(
        f"/api/issues/{issue['id']}",
        json=full_update(issue, status="in_progress", sprint_id=sprint["id"], story_points=5),
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "in_progress"
    assert body["sprint_id"] == sprint["id"]
    assert body["story_points"] == 5


def test_sprint_from_another_project_is_rejected(client, db, auth_headers, project, sprint):
    other = create_approved_project(client, db, auth_headers, "Other", "OT")
    response = create_issue(client, auth_headers, other, sprint_id=sprint["id"])
    assert response.status_code == 400
    assert response.json()["detail"] == "That sprint does not belong to this project"


def test_delete_issue(client, auth_headers, project):
    issue = create_issue(client, auth_headers, project).json()
    assert client.delete(f"/api/issues/{issue['id']}", headers=auth_headers).status_code == 204
    assert client.get(f"/api/issues/{issue['id']}", headers=auth_headers).status_code == 404


def test_other_users_cannot_see_or_change_issues(client, auth_headers, project):
    issue = create_issue(client, auth_headers, project).json()
    bob = login_headers(client, "bob")
    assert client.get(f"/api/issues/{issue['id']}", headers=bob).status_code == 404
    assert client.delete(f"/api/issues/{issue['id']}", headers=bob).status_code == 404
    assert client.get(f"/api/projects/{project['id']}/issues", headers=bob).status_code == 404
