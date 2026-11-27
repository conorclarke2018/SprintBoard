from tests.conftest import login_headers


def start(client, headers, sprint):
    return client.post(f"/api/sprints/{sprint['id']}/start", headers=headers)


def complete(client, headers, sprint):
    return client.post(f"/api/sprints/{sprint['id']}/complete", headers=headers)


def create_sprint(client, headers, project, name="Sprint 2"):
    return client.post(
        f"/api/projects/{project['id']}/sprints",
        json={"name": name, "start_date": "2026-11-16", "end_date": "2026-11-29"},
        headers=headers,
    )


def add_issue(client, headers, project, sprint, status="todo"):
    issue = client.post(
        f"/api/projects/{project['id']}/issues",
        json={"title": f"Issue {status}", "sprint_id": sprint["id"]},
        headers=headers,
    ).json()
    body = {"title": issue["title"], "sprint_id": sprint["id"], "status": status}
    return client.put(f"/api/issues/{issue['id']}", json=body, headers=headers).json()


def test_create_sprint_is_planned(sprint):
    assert sprint["status"] == "planned"
    assert sprint["issue_count"] == 0


def test_end_date_must_be_after_start_date(client, auth_headers, project):
    response = client.post(
        f"/api/projects/{project['id']}/sprints",
        json={"name": "Sprint 1", "start_date": "2026-11-15", "end_date": "2026-11-15"},
        headers=auth_headers,
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "End date must be after the start date"


def test_start_sprint(client, auth_headers, sprint):
    response = start(client, auth_headers, sprint)
    assert response.status_code == 200
    assert response.json()["status"] == "active"


def test_only_one_active_sprint_per_project(client, auth_headers, project, sprint):
    start(client, auth_headers, sprint)
    second = create_sprint(client, auth_headers, project).json()
    response = start(client, auth_headers, second)
    assert response.status_code == 409
    assert "already active" in response.json()["detail"]


def test_cannot_start_a_sprint_twice(client, auth_headers, sprint):
    start(client, auth_headers, sprint)
    assert start(client, auth_headers, sprint).status_code == 400


def test_cannot_complete_a_planned_sprint(client, auth_headers, sprint):
    assert complete(client, auth_headers, sprint).status_code == 400


def test_completing_returns_unfinished_issues_to_backlog(client, auth_headers, project, sprint):
    done = add_issue(client, auth_headers, project, sprint, status="done")
    unfinished = add_issue(client, auth_headers, project, sprint, status="in_progress")
    start(client, auth_headers, sprint)

    response = complete(client, auth_headers, sprint)

    assert response.status_code == 200
    assert response.json()["returned_to_backlog"] == 1
    assert response.json()["sprint"]["status"] == "completed"
    assert response.json()["sprint"]["done_count"] == 1
    issues = {
        issue["id"]: issue
        for issue in client.get(f"/api/projects/{project['id']}/issues", headers=auth_headers).json()
    }
    assert issues[done["id"]]["sprint_id"] == sprint["id"]
    assert issues[unfinished["id"]]["sprint_id"] is None


def test_cannot_add_issues_to_completed_sprint(client, auth_headers, project, sprint):
    start(client, auth_headers, sprint)
    complete(client, auth_headers, sprint)
    response = client.post(
        f"/api/projects/{project['id']}/issues",
        json={"title": "Late work", "sprint_id": sprint["id"]},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Issues cannot be added to a completed sprint"


def test_sprint_counts_issues(client, auth_headers, project, sprint):
    add_issue(client, auth_headers, project, sprint, status="done")
    add_issue(client, auth_headers, project, sprint)
    sprints = client.get(f"/api/projects/{project['id']}/sprints", headers=auth_headers).json()
    assert sprints[0]["issue_count"] == 2
    assert sprints[0]["done_count"] == 1


def update(client, headers, sprint, **changes):
    body = {"name": sprint["name"], "start_date": sprint["start_date"], "end_date": sprint["end_date"]}
    return client.put(f"/api/sprints/{sprint['id']}", json={**body, **changes}, headers=headers)


def test_owner_can_edit_sprint(client, auth_headers, sprint):
    response = update(client, auth_headers, sprint, name="Sprint One", goal="Ship login")
    assert response.status_code == 200
    assert response.json()["name"] == "Sprint One"
    assert response.json()["goal"] == "Ship login"
    assert response.json()["status"] == "planned"


def test_edit_sprint_is_validated(client, auth_headers, sprint):
    response = update(client, auth_headers, sprint, end_date=sprint["start_date"])
    assert response.status_code == 422
    assert response.json()["detail"] == "End date must be after the start date"


def test_completed_sprint_cannot_be_edited(client, auth_headers, sprint):
    start(client, auth_headers, sprint)
    complete(client, auth_headers, sprint)
    response = update(client, auth_headers, sprint, name="Rewritten")
    assert response.status_code == 400
    assert response.json()["detail"] == "A completed sprint cannot be edited"


def test_other_users_cannot_edit_or_start_sprint(client, sprint):
    bob = login_headers(client, "bob")
    assert update(client, bob, sprint, name="Bob's sprint").status_code == 403
    assert start(client, bob, sprint).status_code == 403


def test_admin_delete_sprint_returns_issues_to_backlog(client, auth_headers, admin_headers, project, sprint):
    issue = add_issue(client, auth_headers, project, sprint)

    response = client.delete(f"/api/sprints/{sprint['id']}", headers=admin_headers)

    assert response.status_code == 204
    assert client.get(f"/api/projects/{project['id']}/sprints", headers=auth_headers).json() == []
    assert client.get(f"/api/issues/{issue['id']}", headers=auth_headers).json()["sprint_id"] is None


def test_regular_user_cannot_delete_sprint(client, auth_headers, sprint):
    response = client.delete(f"/api/sprints/{sprint['id']}", headers=auth_headers)
    assert response.status_code == 403
