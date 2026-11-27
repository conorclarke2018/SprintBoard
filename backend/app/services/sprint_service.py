"""Sprint rules: one active sprint per project; completing returns unfinished work."""

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.models import Project, Sprint, User
from app.models.enums import IssueStatus, SprintStatus
from app.schemas.sprint import SprintCreate, SprintUpdate
from app.services.project_service import can_view

logger = logging.getLogger(__name__)


def get_sprint(db: Session, sprint_id: int, user: User) -> Sprint:
    """Find a sprint the user is allowed to see."""
    sprint = db.get(Sprint, sprint_id)
    if sprint is None or not can_view(sprint.project, user):
        raise NotFoundError("Sprint not found")
    return sprint


def create_sprint(db: Session, project: Project, data: SprintCreate) -> Sprint:
    sprint = Sprint(**data.model_dump(), project_id=project.id)
    db.add(sprint)
    db.commit()
    db.refresh(sprint)
    logger.info("Sprint '%s' created in %s", sprint.name, project.key)
    return sprint


def update_sprint(db: Session, sprint: Sprint, data: SprintUpdate) -> Sprint:
    """Change a sprint's name, goal or dates. Completed sprints are kept as a record."""
    if sprint.status == SprintStatus.COMPLETED:
        raise BusinessRuleError("A completed sprint cannot be edited")

    for field, value in data.model_dump().items():
        setattr(sprint, field, value)
    db.commit()
    db.refresh(sprint)
    logger.info("Sprint '%s' updated in %s", sprint.name, sprint.project.key)
    return sprint


def delete_sprint(db: Session, sprint: Sprint) -> int:
    """Delete a sprint and return its issues to the backlog. Returns how many moved."""
    moved = len(sprint.issues)
    for issue in sprint.issues:
        issue.sprint = None
    logger.info("Sprint '%s' deleted from %s; %d issue(s) returned to backlog", sprint.name, sprint.project.key, moved)
    db.delete(sprint)
    db.commit()
    return moved


def start_sprint(db: Session, sprint: Sprint) -> Sprint:
    if sprint.status != SprintStatus.PLANNED:
        raise BusinessRuleError("Only a planned sprint can be started")

    active = db.scalar(
        select(Sprint).where(
            Sprint.project_id == sprint.project_id, Sprint.status == SprintStatus.ACTIVE
        )
    )
    if active is not None:
        raise ConflictError(f"'{active.name}' is already active. Complete it first.")

    sprint.status = SprintStatus.ACTIVE
    db.commit()
    db.refresh(sprint)
    logger.info("Sprint '%s' started", sprint.name)
    return sprint


def complete_sprint(db: Session, sprint: Sprint) -> int:
    """Close the sprint and move unfinished issues back to the backlog. Returns how many moved."""
    if sprint.status != SprintStatus.ACTIVE:
        raise BusinessRuleError("Only an active sprint can be completed")

    unfinished = [issue for issue in sprint.issues if issue.status != IssueStatus.DONE]
    for issue in unfinished:
        issue.sprint = None
    sprint.status = SprintStatus.COMPLETED
    db.commit()
    db.refresh(sprint)
    logger.info("Sprint '%s' completed; %d issue(s) returned to backlog", sprint.name, len(unfinished))
    return len(unfinished)
