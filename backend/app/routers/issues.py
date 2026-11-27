from fastapi import APIRouter, status

from app.core.dependencies import AdminUser, ApprovedProject, CurrentUser, DbSession, ManagedApprovedProject
from app.schemas.issue import IssueCreate, IssueRead, IssueUpdate
from app.services import issue_service, project_service

router = APIRouter(prefix="/api", tags=["issues"])


@router.get("/projects/{project_id}/issues", response_model=list[IssueRead])
def list_issues(project: ApprovedProject):
    return project.issues


@router.post(
    "/projects/{project_id}/issues", response_model=IssueRead, status_code=status.HTTP_201_CREATED
)
def create_issue(data: IssueCreate, project: ManagedApprovedProject, db: DbSession):
    return issue_service.create_issue(db, project, data)


@router.get("/issues/{issue_id}", response_model=IssueRead)
def get_issue(issue_id: int, db: DbSession, user: CurrentUser):
    return issue_service.get_issue(db, issue_id, user)


@router.put("/issues/{issue_id}", response_model=IssueRead)
def update_issue(issue_id: int, data: IssueUpdate, db: DbSession, user: CurrentUser):
    issue = issue_service.get_issue(db, issue_id, user)
    project_service.require_manage(issue.project, user)
    return issue_service.update_issue(db, issue, data)


@router.delete("/issues/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_issue(issue_id: int, db: DbSession, admin: AdminUser):
    """Admins only: regular users can create, read and update but not delete."""
    issue = issue_service.get_issue(db, issue_id, admin)
    issue_service.delete_issue(db, issue)
