"""Shared FastAPI dependencies: database session, current user and owned project."""

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


def get_owned_project(project_id: int, db: DbSession, user: CurrentUser) -> Project:
    return project_service.get_project(db, project_id, user)


OwnedProject = Annotated[Project, Depends(get_owned_project)]


def get_approved_project(project: OwnedProject) -> Project:
    return project_service.require_approved(project)


ApprovedProject = Annotated[Project, Depends(get_approved_project)]
