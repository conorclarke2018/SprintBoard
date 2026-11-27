"""Shared FastAPI dependencies: database session, current user and project access."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, ForbiddenError
from app.core.security import decode_access_token
from app.database import get_db
from app.models import Project, User
from app.services import project_service

bearer_scheme = HTTPBearer(auto_error=False)

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User:
    if credentials is None:
        raise AuthenticationError("Please log in to continue")

    user_id = decode_access_token(credentials.credentials)
    user = db.get(User, user_id) if user_id is not None else None
    if user is None or not user.is_approved:
        raise AuthenticationError("Your session has expired. Please log in again")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_admin(user: CurrentUser) -> User:
    if not user.is_admin:
        raise ForbiddenError("Only admins can do this")
    return user


AdminUser = Annotated[User, Depends(get_current_admin)]


def get_visible_project(project_id: int, db: DbSession, user: CurrentUser) -> Project:
    """A project the user may look at (their own, or any approved project)."""
    return project_service.get_project(db, project_id, user)


VisibleProject = Annotated[Project, Depends(get_visible_project)]


def get_managed_project(project: VisibleProject, user: CurrentUser) -> Project:
    """A project the user may change (admins and the owner)."""
    project_service.require_manage(project, user)
    return project


ManagedProject = Annotated[Project, Depends(get_managed_project)]


def get_approved_project(project: VisibleProject) -> Project:
    """A visible project whose issues and sprints can be read."""
    return project_service.require_approved(project)


ApprovedProject = Annotated[Project, Depends(get_approved_project)]


def get_managed_approved_project(project: ManagedProject) -> Project:
    """An approved project the user may add issues and sprints to."""
    return project_service.require_approved(project)


ManagedApprovedProject = Annotated[Project, Depends(get_managed_approved_project)]
