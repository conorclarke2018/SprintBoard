"""Admin-only user management: approve accounts, change roles and delete accounts."""

import logging

from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models import User
from app.models.enums import UserRole

logger = logging.getLogger(__name__)


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
