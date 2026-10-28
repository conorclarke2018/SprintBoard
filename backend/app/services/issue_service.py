"""Issue rules: numbering, sprint and assignee checks."""

import logging

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models import Issue, Project, Sprint, User
from app.models.enums import SprintStatus
from app.schemas.issue import IssueCreate, IssueUpdate
from app.services.project_service import can_manage

logger = logging.getLogger(__name__)


def get_issue(db: Session, issue_id: int, user: User) -> Issue:
    issue = db.get(Issue, issue_id)
    if issue is None or not can_manage(issue.project, user):
        raise NotFoundError("Issue not found")
    return issue


def _check_links(db: Session, project: Project, data: IssueCreate) -> None:
    """The sprint must belong to the same project and still be open; the assignee must exist."""
    if data.sprint_id is not None:
        sprint = db.get(Sprint, data.sprint_id)
        if sprint is None or sprint.project_id != project.id:
            raise BusinessRuleError("That sprint does not belong to this project")
        if sprint.status == SprintStatus.COMPLETED:
            raise BusinessRuleError("Issues cannot be added to a completed sprint")

    if data.assignee_id is not None and db.get(User, data.assignee_id) is None:
        raise BusinessRuleError("The selected assignee does not exist")


def _next_issue_number(db: Session, project: Project) -> int:
    highest = db.scalar(select(func.max(Issue.number)).where(Issue.project_id == project.id))
    return (highest or 0) + 1


def create_issue(db: Session, project: Project, data: IssueCreate) -> Issue:
    _check_links(db, project, data)
    issue = Issue(**data.model_dump(), project_id=project.id, number=_next_issue_number(db, project))
    db.add(issue)
    db.commit()
    db.refresh(issue)
    logger.info("Issue %s created", issue.key)
    return issue


def update_issue(db: Session, issue: Issue, data: IssueUpdate) -> Issue:
    _check_links(db, issue.project, data)
    for field, value in data.model_dump().items():
        setattr(issue, field, value)
    db.commit()
    db.refresh(issue)
    return issue


def delete_issue(db: Session, issue: Issue) -> None:
    logger.info("Issue %s deleted", issue.key)
    db.delete(issue)
    db.commit()
