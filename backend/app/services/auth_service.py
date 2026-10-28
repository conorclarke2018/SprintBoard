"""Registration, login and user lookups."""

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, ConflictError, ForbiddenError
from app.core.security import hash_password, verify_password
from app.models import User
from app.models.enums import UserRole
from app.schemas.user import UserCreate, UserLogin

logger = logging.getLogger(__name__)


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username))


def register_user(db: Session, data: UserCreate) -> User:
    """The first account becomes an approved admin; later accounts wait for an admin's approval."""
    if get_user_by_username(db, data.username):
        raise ConflictError("That username is already taken")

    is_first_user = db.scalar(select(User).limit(1)) is None
    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        role=UserRole.ADMIN if is_first_user else UserRole.USER,
        is_approved=is_first_user,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    if is_first_user:
        logger.info("First account %s registered as admin", user.username)
    else:
        logger.info("New user registered and waiting for approval: %s", user.username)
    return user


def authenticate(db: Session, data: UserLogin) -> User:
    user = get_user_by_username(db, data.username)
    if user is None or not verify_password(data.password, user.password_hash):
        logger.warning("Failed login attempt for username '%s'", data.username)
        raise AuthenticationError("Incorrect username or password")
    if not user.is_approved:
        logger.warning("Login blocked for unapproved user '%s'", user.username)
        raise ForbiddenError("Your account is waiting for an admin to approve it")
    logger.info("User logged in: %s", user.username)
    return user


def list_users(db: Session) -> list[User]:
    """Approved users only, e.g. for the assignee list."""
    query = select(User).where(User.is_approved.is_(True)).order_by(User.username)
    return list(db.scalars(query))
