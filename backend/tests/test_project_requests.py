def request_project(client, headers, key="WEB"):
    return client.post("/api/projects", json={"name": "Website", "key": key}, headers=headers).json()


def approve(client, headers, project):
    return client.post(f"/api/admin/projects/{project['id']}/approve", headers=headers)


def reject(client, headers, project, reason=None):
    return client.post(
        f"/api/admin/projects/{project['id']}/reject", json={"reason": reason}, headers=headers
    )


def test_user_project_starts_as_pending_request(client, auth_headers):
    assert request_project(client, auth_headers)["status"] == "pending"


def test_admin_project_is_approved_straight_away(client, admin_headers):
    assert request_project(client, admin_headers)["status"] == "approved"


def test_pending_project_cannot_have_issues_or_sprints(client, auth_headers):
    project = request_project(client, auth_headers)
    issue = client.post(
        f"/api/projects/{project['id']}/issues", json={"title": "Too early"}, headers=auth_headers
    )
    assert issue.status_code == 403
    assert issue.json()["detail"] == "This project has not been approved by an admin yet"
    sprints = client.get(f"/api/projects/{project['id']}/sprints", headers=auth_headers)
    assert sprints.status_code == 403


def test_admin_sees_pending_requests(client, auth_headers, admin_headers):
    request_project(client, auth_headers)
    requests = client.get("/api/admin/project-requests", headers=admin_headers).json()
    assert [(r["key"], r["owner"]["username"]) for r in requests] == [("WEB", "alice")]


def test_users_cannot_review_requests(client, auth_headers):
    project = request_project(client, auth_headers)
    assert client.get("/api/admin/project-requests", headers=auth_headers).status_code == 403
    assert approve(client, auth_headers, project).status_code == 403


def test_approved_project_can_be_used(client, auth_headers, admin_headers):
    project = request_project(client, auth_headers)
    assert approve(client, admin_headers, project).json()["status"] == "approved"
    issue = client.post(
        f"/api/projects/{project['id']}/issues", json={"title": "First issue"}, headers=auth_headers
    )
    assert issue.status_code == 201
    assert client.get("/api/admin/project-requests", headers=admin_headers).json() == []


def test_rejected_project_keeps_the_reason(client, auth_headers, admin_headers):
    project = request_project(client, auth_headers)
    body = reject(client, admin_headers, project, "We already have a website project").json()
    assert body["status"] == "rejected"
    assert body["review_note"] == "We already have a website project"


def test_request_can_only_be_reviewed_once(client, auth_headers, admin_headers):
    project = request_project(client, auth_headers)
    approve(client, admin_headers, project)
    response = reject(client, admin_headers, project)
    assert response.status_code == 400
    assert response.json()["detail"] == "Only pending requests can be approved or rejected"


def test_editing_a_rejected_request_resubmits_it(client, auth_headers, admin_headers):
    project = request_project(client, auth_headers)
    reject(client, admin_headers, project, "Name is unclear")
    response = client.put(
        f"/api/projects/{project['id']}",
        json={"name": "Company website", "description": "Public marketing site"},
        headers=auth_headers,
    )
    assert response.json()["status"] == "pending"
    assert response.json()["review_note"] is None


def test_reject_reason_is_limited(client, auth_headers, admin_headers):
    project = request_project(client, auth_headers)
    response = reject(client, admin_headers, project, "x" * 301)
    assert response.status_code == 422
    assert response.json()["detail"].startswith("Reason:")
