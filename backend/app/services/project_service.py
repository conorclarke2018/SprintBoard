"""Project rules: users request projects, admins approve or reject them and can manage every project."""

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, ConflictError, ForbiddenError, NotFoundError
from app.models import Project, User
from app.models.enums import ProjectStatus
from app.schemas.project import ProjectCreate, ProjectUpdate

logger = logging.getLogger(__name__)


def can_manage(project: Project, user: User) -> bool:
    """The single access rule for a project and everything inside it."""
    return user.is_admin or project.owner_id == user.id


def list_projects(db: Session, user: User) -> list[Project]:
    query = select(Project).order_by(Project.name)
    if not user.is_admin:
        query = query.where(Project.owner_id == user.id)
    return list(db.scalars(query))


def list_requests(db: Session) -> list[Project]:
    query = select(Project).where(Project.status == ProjectStatus.PENDING).order_by(Project.created_at)
    return list(db.scalars(query))


def get_project(db: Session, project_id: int, user: User) -> Project:
    project = db.get(Project, project_id)
    # Report "not found" rather than "forbidden" so other users' projects stay hidden.
    if project is None or not can_manage(project, user):
        raise NotFoundError("Project not found")
    return project


def require_approved(project: Project) -> Project:
    """Issues and sprints can only be added once an admin has approved the project."""
    if not project.is_approved:
        raise ForbiddenError("This project has not been approved by an admin yet")
    return project


def create_project(db: Session, data: ProjectCreate, owner: User) -> Project:
    """Admins' projects are approved straight away; everyone else's become a request."""
    if db.scalar(select(Project).where(Project.key == data.key)):
        raise ConflictError(f"Project key '{data.key}' is already in use")

    status = ProjectStatus.APPROVED if owner.is_admin else ProjectStatus.PENDING
    project = Project(**data.model_dump(), owner_id=owner.id, status=status)
    db.add(project)
    db.commit()
    db.refresh(project)
    action = "created" if project.is_approved else "requested"
    logger.info("Project %s %s by %s", project.key, action, owner.username)
    return project


def update_project(db: Session, project: Project, data: ProjectUpdate, user: User) -> Project:
    project.name = data.name
    project.description = data.description
    # Editing a rejected request sends it back to the admins for another look.
    if project.status == ProjectStatus.REJECTED and not user.is_admin:
        project.status = ProjectStatus.PENDING
        project.review_note = None
        logger.info("Project request %s resubmitted by %s", project.key, user.username)
    db.commit()
    db.refresh(project)
    return project


def _review(db: Session, project: Project, status: ProjectStatus, note: str | None, admin: User) -> Project:
    if project.status != ProjectStatus.PENDING:
        raise BusinessRuleError("Only pending requests can be approved or rejected")

    project.status = status
    project.review_note = note
    db.commit()
    db.refresh(project)
    logger.info("Admin %s %s project request %s", admin.username, status, project.key)
    return project


def approve_project(db: Session, project: Project, admin: User) -> Project:
    return _review(db, project, ProjectStatus.APPROVED, None, admin)


def reject_project(db: Session, project: Project, reason: str | None, admin: User) -> Project:
    return _review(db, project, ProjectStatus.REJECTED, reason, admin)


def delete_project(db: Session, project: Project) -> None:
    logger.info("Project %s deleted", project.key)
    db.delete(project)
    db.commit()
