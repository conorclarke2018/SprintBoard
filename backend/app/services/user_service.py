"""Admin-only user management: approve accounts, change roles and delete accounts."""

import logging

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.error_handlers import format_validation_errors
from app.core.exceptions import BusinessRuleError, NotFoundError
from app.core.security import hash_password
from app.models import User
from app.models.enums import UserRole
from app.schemas.user import UserCreate

logger = logging.getLogger(__name__)


def ensure_admin_account(db: Session, username: str, password: str) -> User | None:
    """Make sure the configured admin exists, is approved and uses the configured password."""
    try:
        data = UserCreate(username=username, password=password)
    except ValidationError as error:
        reason = format_validation_errors(error.errors())
        logger.error("ADMIN_USERNAME/ADMIN_PASSWORD are invalid: %s", reason)
        return None

    user = db.scalar(select(User).where(User.username == data.username))
    if user is None:
        user = User(username=data.username)
        db.add(user)
        logger.info("Created admin account %s from environment settings", data.username)
    user.password_hash = hash_password(data.password)
    user.role = UserRole.ADMIN
    user.is_approved = True
    db.commit()
    return user


def get_user(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError("User not found")
    return user


def approve_user(db: Session, user: User, admin: User) -> User:
    if user.is_approved:
        raise BusinessRuleError("This account is already approved")

    user.is_approved = True
    db.commit()
    db.refresh(user)
    logger.info("Admin %s approved account %s", admin.username, user.username)
    return user


def set_role(db: Session, user: User, role: UserRole, admin: User) -> User:
    # Admins cannot demote or delete themselves, so there is always at least one admin.
    if user.id == admin.id:
        raise BusinessRuleError("You cannot change your own role")

    user.role = role
    db.commit()
    db.refresh(user)
    logger.info("Admin %s set %s's role to %s", admin.username, user.username, role)
    return user


def delete_user(db: Session, user: User, admin: User) -> None:
    """Delete an account and the projects it owns. Issues assigned to it become unassigned."""
    if user.id == admin.id:
        raise BusinessRuleError("You cannot delete your own account")

    logger.info("Admin %s deleted user %s", admin.username, user.username)
    db.delete(user)
    db.commit()
